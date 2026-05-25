from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.models.resena import Resena
from app.models.solicitud import Solicitud
from sqlalchemy import desc
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.models.tecnico_comuna import TecnicoComuna
from app.models.comuna import Comuna
from app.models.tecnico_servicio import TecnicoServicio

from app.database import get_db
from app.schemas.tecnico_schema import TecnicoCreate, TecnicoUpdate, TecnicoResponse
from app.services import tecnico_service

router = APIRouter(
    prefix="/tecnicos",
    tags=["Técnicos"]
)

@router.post("/", response_model=TecnicoResponse)
def crear_tecnico(tecnico: TecnicoCreate, db: Session = Depends(get_db)):
    nuevo_tecnico = tecnico_service.crear_tecnico(db, tecnico)

    if not nuevo_tecnico:
        raise HTTPException(status_code=400, detail="El técnico ya existe")

    return nuevo_tecnico


@router.get("/", response_model=List[TecnicoResponse])
def listar_tecnicos(db: Session = Depends(get_db)):
    return tecnico_service.listar_tecnicos(db)


@router.get("/buscar")
def buscar_tecnicos_por_servicio_comuna(
    servicio_id: int,
    comuna_id: int,
    db: Session = Depends(get_db)
):
    tecnicos = db.query(Tecnico).join(
        TecnicoServicio,
        Tecnico.usuario_rut == TecnicoServicio.tecnico_usuario_rut
    ).join(
        TecnicoComuna,
        Tecnico.usuario_rut == TecnicoComuna.tecnico_usuario_rut
    ).filter(
        TecnicoServicio.servicio_id_servicio == servicio_id,
        TecnicoComuna.comuna_id_comuna == comuna_id,
        Tecnico.tecnico_verificado == True
    ).all()

    return tecnicos


@router.get("/publicos/perfiles")
def listar_perfiles_publicos_tecnicos(db: Session = Depends(get_db)):
    tecnicos = db.query(Tecnico).join(
        Usuario,
        Usuario.rut == Tecnico.usuario_rut
    ).filter(
        Tecnico.tecnico_verificado == True
    ).all()

    return [
        {
            "usuario_rut": tecnico.usuario_rut,
            "nombre_completo": tecnico.usuario.nombre_completo if tecnico.usuario else "Tecnico FixYa",
            "correo": tecnico.usuario.correo if tecnico.usuario else None,
            "telefono": tecnico.usuario.telefono if tecnico.usuario else None,
            "descripcion_perfil": tecnico.descripcion_perfil,
            "experiencia_anios": tecnico.experiencia_anios,
            "nivel_tecnico": tecnico.nivel_tecnico,
            "tecnico_verificado": tecnico.tecnico_verificado,
        }
        for tecnico in tecnicos
    ]

@router.get("/{rut}", response_model=TecnicoResponse)
def obtener_tecnico(rut: str, db: Session = Depends(get_db)):
    tecnico = tecnico_service.obtener_tecnico(db, rut)

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    return tecnico


@router.put("/{rut}", response_model=TecnicoResponse)
def actualizar_tecnico(rut: str, tecnico: TecnicoUpdate, db: Session = Depends(get_db)):
    tecnico_actualizado = tecnico_service.actualizar_tecnico(db, rut, tecnico)

    if not tecnico_actualizado:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    return tecnico_actualizado


@router.delete("/{rut}")
def eliminar_tecnico(rut: str, db: Session = Depends(get_db)):
    tecnico_eliminado = tecnico_service.eliminar_tecnico(db, rut)

    if not tecnico_eliminado:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    return {"mensaje": "Técnico eliminado correctamente"}
@router.get("/{rut}/rating")
def obtener_rating_tecnico(
    rut: str,
    db: Session = Depends(get_db)
):
    promedio = db.query(
        func.avg(Resena.calificacion)
    ).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).scalar()

    total = db.query(Resena).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).count()

    return {
        "tecnico_usuario_rut": rut,
        "promedio_calificacion": round(float(promedio), 1) if promedio else 0,
        "total_resenas": total
    }
    
@router.get("/top-rating")
def obtener_top_tecnicos(
    db: Session = Depends(get_db)
):
    resultados = db.query(
        Solicitud.tecnico_usuario_rut,
        func.avg(Resena.calificacion).label("promedio"),
        func.count(Resena.id_resena).label("total_resenas")
    ).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Resena.resena_activa == "S"
    ).group_by(
        Solicitud.tecnico_usuario_rut
    ).order_by(
        desc("promedio")
    ).limit(10).all()

    return [
        {
            "tecnico_usuario_rut": r.tecnico_usuario_rut,
            "promedio_calificacion": round(float(r.promedio), 1),
            "total_resenas": r.total_resenas
        }
        for r in resultados
    ]
@router.get("/{rut}/perfil")
def obtener_perfil_tecnico(
    rut: str,
    db: Session = Depends(get_db)
):
    tecnico = db.query(Tecnico).filter(
        Tecnico.usuario_rut == rut
    ).first()

    if not tecnico:
        raise HTTPException(
            status_code=404,
            detail="Técnico no encontrado"
        )

    promedio = db.query(
        func.avg(Resena.calificacion)
    ).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).scalar()

    total = db.query(Resena).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).count()

    return {
        "usuario_rut": tecnico.usuario_rut,
        "descripcion_perfil": tecnico.descripcion_perfil,
        "experiencia_anios": tecnico.experiencia_anios,
        "nivel_tecnico": tecnico.nivel_tecnico,
        "tecnico_verificado": tecnico.tecnico_verificado,
        "promedio_calificacion": round(float(promedio), 1) if promedio else 0,
        "total_resenas": total
    }
@router.post("/{rut}/comunas/{id_comuna}")
def asignar_comuna_tecnico(
    rut: str,
    id_comuna: int,
    db: Session = Depends(get_db)
):
    tecnico = db.query(Tecnico).filter(
        Tecnico.usuario_rut == rut
    ).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    comuna = db.query(Comuna).filter(
        Comuna.id_comuna == id_comuna
    ).first()

    if not comuna:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")

    existe = db.query(TecnicoComuna).filter(
        TecnicoComuna.tecnico_usuario_rut == rut,
        TecnicoComuna.comuna_id_comuna == id_comuna
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="El técnico ya atiende esta comuna")

    nueva = TecnicoComuna(
        tecnico_usuario_rut=rut,
        comuna_id_comuna=id_comuna
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "mensaje": "Comuna asignada correctamente",
        "tecnico_usuario_rut": rut,
        "comuna_id_comuna": id_comuna
    }  
@router.get("/{rut}/comunas")
def listar_comunas_tecnico(
    rut: str,
    db: Session = Depends(get_db)
):
    comunas = db.query(Comuna).join(
        TecnicoComuna,
        Comuna.id_comuna == TecnicoComuna.comuna_id_comuna
    ).filter(
        TecnicoComuna.tecnico_usuario_rut == rut
    ).all()

    return comunas

@router.delete("/{rut}/comunas/{id_comuna}")
def eliminar_comuna_tecnico(
    rut: str,
    id_comuna: int,
    db: Session = Depends(get_db)
):
    tecnico_comuna = db.query(TecnicoComuna).filter(
        TecnicoComuna.tecnico_usuario_rut == rut,
        TecnicoComuna.comuna_id_comuna == id_comuna
    ).first()

    if not tecnico_comuna:
        raise HTTPException(
            status_code=404,
            detail="Comuna no asignada al técnico"
        )

    db.delete(tecnico_comuna)
    db.commit()

    return {
        "mensaje": "Comuna eliminada del técnico correctamente",
        "tecnico_usuario_rut": rut,
        "comuna_id_comuna": id_comuna
    }
    
@router.get("/{rut}/dashboard")
def obtener_dashboard_tecnico(
    rut: str,
    db: Session = Depends(get_db)
):
    solicitudes_asignadas = db.query(Solicitud).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Solicitud.estado_trabajo == "ASIGNADO"
    ).count()

    solicitudes_en_proceso = db.query(Solicitud).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Solicitud.estado_trabajo == "EN_PROCESO"
    ).count()

    solicitudes_finalizadas = db.query(Solicitud).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Solicitud.estado_trabajo == "FINALIZADO"
    ).count()

    ingresos_totales = db.query(
        func.sum(Solicitud.costo_final)
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Solicitud.estado_trabajo == "FINALIZADO"
    ).scalar()

    promedio = db.query(
        func.avg(Resena.calificacion)
    ).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).scalar()

    total_resenas = db.query(Resena).join(
        Solicitud,
        Solicitud.id_solicitud == Resena.solicitud_id_solicitud
    ).filter(
        Solicitud.tecnico_usuario_rut == rut,
        Resena.resena_activa == "S"
    ).count()

    return {
        "tecnico_usuario_rut": rut,
        "solicitudes_asignadas": solicitudes_asignadas,
        "solicitudes_en_proceso": solicitudes_en_proceso,
        "solicitudes_finalizadas": solicitudes_finalizadas,
        "ingresos_totales": float(ingresos_totales) if ingresos_totales else 0,
        "promedio_calificacion": round(float(promedio), 1) if promedio else 0,
        "total_resenas": total_resenas
    }
