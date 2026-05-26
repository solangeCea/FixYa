from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.schemas.notificacion_schema import NotificacionResponse


router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"]
)


@router.get("/", response_model=list[NotificacionResponse])
def listar_mis_notificaciones(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == current_user["correo"]
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    notificaciones = db.query(Notificacion).filter(
        Notificacion.usuario_rut == usuario.rut
    ).order_by(
        Notificacion.fecha_creacion.desc()
    ).all()

    return notificaciones


@router.put("/{id_notificacion}/leer")
def marcar_notificacion_como_leida(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == current_user["correo"]
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    notificacion = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion,
        Notificacion.usuario_rut == usuario.rut
    ).first()

    if not notificacion:
        raise HTTPException(
            status_code=404,
            detail="Notificación no encontrada"
        )

    notificacion.leida = True

    db.commit()
    db.refresh(notificacion)

    return {
        "mensaje": "Notificación marcada como leída",
        "id_notificacion": notificacion.id_notificacion
    }


@router.put("/leer-todas")
def marcar_todas_como_leidas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == current_user["correo"]
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    notificaciones = db.query(Notificacion).filter(
        Notificacion.usuario_rut == usuario.rut,
        Notificacion.leida == False
    ).all()

    for notificacion in notificaciones:
        notificacion.leida = True

    db.commit()

    return {
        "mensaje": "Todas las notificaciones fueron marcadas como leídas",
        "total": len(notificaciones)
    }
