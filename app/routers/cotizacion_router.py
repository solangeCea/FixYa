from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user, requiere_rol
from app.models.solicitud import Solicitud
from app.models.usuario import Usuario
from app.schemas.cotizacion_schema import (
    CotizacionCreate,
    CotizacionUpdate,
    CotizacionResponse,
)
from app.services import cotizacion_service

router = APIRouter(
    prefix="/cotizaciones",
    tags=["Cotizaciones"]
)


def obtener_usuario_por_token(db: Session, usuario_actual: dict):
    return db.query(Usuario).filter(
        Usuario.correo == usuario_actual["correo"]
    ).first()


@router.post("/", response_model=CotizacionResponse)
def crear_cotizacion(
    cotizacion: CotizacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requiere_rol(["TECNICO"]))
):
    usuario = obtener_usuario_por_token(db, usuario_actual)

    if not usuario or usuario.rut != cotizacion.tecnico_usuario_rut:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes crear cotizaciones propias"
        )

    nueva = cotizacion_service.crear_cotizacion(db, cotizacion)

    if nueva is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if nueva == "TECNICO_NO_ASIGNADO":
        raise HTTPException(
            status_code=400,
            detail="La solicitud no esta asignada a este tecnico"
        )

    return nueva


@router.get("/", response_model=List[CotizacionResponse])
def listar_cotizaciones(db: Session = Depends(get_db)):
    return cotizacion_service.listar_cotizaciones(db)


@router.get("/solicitud/{id_solicitud}", response_model=List[CotizacionResponse])
def listar_por_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(get_current_user)
):
    solicitud = db.query(Solicitud).filter(
        Solicitud.id_solicitud == id_solicitud
    ).first()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    usuario = obtener_usuario_por_token(db, usuario_actual)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if usuario_actual["tipo_usuario"] == "CLIENTE" and solicitud.usuario_rut != usuario.rut:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver cotizaciones de otra solicitud"
        )

    if usuario_actual["tipo_usuario"] == "TECNICO" and solicitud.tecnico_usuario_rut != usuario.rut:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver cotizaciones de otra solicitud"
        )

    return cotizacion_service.listar_por_solicitud(db, id_solicitud)


@router.get("/{id_cotizacion}", response_model=CotizacionResponse)
def obtener_cotizacion(id_cotizacion: int, db: Session = Depends(get_db)):
    cotizacion = cotizacion_service.obtener_cotizacion(db, id_cotizacion)

    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    return cotizacion


@router.put("/{id_cotizacion}", response_model=CotizacionResponse)
def actualizar_cotizacion(
    id_cotizacion: int,
    cotizacion: CotizacionUpdate,
    db: Session = Depends(get_db)
):
    cotizacion_actualizada = cotizacion_service.actualizar_cotizacion(
        db,
        id_cotizacion,
        cotizacion
    )

    if not cotizacion_actualizada:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    return cotizacion_actualizada


@router.put("/{id_cotizacion}/aceptar", response_model=CotizacionResponse)
def aceptar_cotizacion(
    id_cotizacion: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requiere_rol(["CLIENTE"]))
):
    cotizacion_actual = cotizacion_service.obtener_cotizacion(db, id_cotizacion)

    if not cotizacion_actual:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    solicitud = db.query(Solicitud).filter(
        Solicitud.id_solicitud == cotizacion_actual.solicitud_id_solicitud
    ).first()
    usuario = obtener_usuario_por_token(db, usuario_actual)

    if not solicitud or not usuario or solicitud.usuario_rut != usuario.rut:
        raise HTTPException(status_code=403, detail="No puedes aceptar esta cotizacion")

    cotizacion = cotizacion_service.aceptar_cotizacion(db, id_cotizacion)

    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    return cotizacion


@router.put("/{id_cotizacion}/rechazar", response_model=CotizacionResponse)
def rechazar_cotizacion(
    id_cotizacion: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(requiere_rol(["CLIENTE"]))
):
    cotizacion_actual = cotizacion_service.obtener_cotizacion(db, id_cotizacion)

    if not cotizacion_actual:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    solicitud = db.query(Solicitud).filter(
        Solicitud.id_solicitud == cotizacion_actual.solicitud_id_solicitud
    ).first()
    usuario = obtener_usuario_por_token(db, usuario_actual)

    if not solicitud or not usuario or solicitud.usuario_rut != usuario.rut:
        raise HTTPException(status_code=403, detail="No puedes rechazar esta cotizacion")

    cotizacion = cotizacion_service.rechazar_cotizacion(db, id_cotizacion)

    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    return cotizacion


@router.put("/{id_cotizacion}/anular", response_model=CotizacionResponse)
def anular_cotizacion(
    id_cotizacion: int,
    motivo: str,
    db: Session = Depends(get_db)
):
    cotizacion = cotizacion_service.anular_cotizacion(db, id_cotizacion, motivo)

    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    return cotizacion
