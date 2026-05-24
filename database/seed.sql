-- REGIONES
INSERT INTO region (id_region, nombre_region)
VALUES
(1, 'Biobío')
ON CONFLICT (id_region) DO NOTHING;

-- COMUNAS
INSERT INTO comuna (id_comuna, nombre_comuna, region_id_region)
VALUES
(11, 'Concepción', 1),
(12, 'Talcahuano', 1),
(13, 'San Pedro de la Paz', 1)
ON CONFLICT (id_comuna) DO NOTHING;

-- SERVICIOS
INSERT INTO servicio (
  id_servicio,
  nombre_servicio,
  descripcion_servicio,
  servicio_activo
)
VALUES
(1, 'Electricidad', 'Servicios eléctricos', true),
(2, 'Gasfitería', 'Reparaciones de agua y gas', true),
(3, 'Carpintería', 'Trabajos de madera', true),
(4, 'Cerrajería', 'Servicios de cerraduras', true)
ON CONFLICT (id_servicio) DO NOTHING;

-- USUARIO ADMIN
-- Contraseña real: admin123
INSERT INTO usuario (
  rut,
  nombre_completo,
  fecha_nacimiento,
  genero,
  correo,
  telefono,
  contrasena,
  estado_usuario,
  comuna_id_comuna,
  tipo_usuario
)
VALUES (
  '11111111-1',
  'Administrador FixYa',
  '1990-01-01',
  'Masculino',
  'admin@fixya.cl',
  '999999999',
  '$2y$12$yRSpEk4TrjXeHrte.UhMrOCTSTy2G8N.xVuKPs7k0isZpnic46q8q',
  true,
  11,
  'ADMIN'
)
ON CONFLICT (rut) DO UPDATE SET
  correo = EXCLUDED.correo,
  contrasena = EXCLUDED.contrasena,
  tipo_usuario = EXCLUDED.tipo_usuario,
  estado_usuario = EXCLUDED.estado_usuario;

-- USUARIO CLIENTE
-- Contraseña real: cliente123
INSERT INTO usuario (
  rut,
  nombre_completo,
  fecha_nacimiento,
  genero,
  correo,
  telefono,
  contrasena,
  estado_usuario,
  comuna_id_comuna,
  tipo_usuario
)
VALUES (
  '22222222-2',
  'Cliente Demo',
  '1998-05-10',
  'Femenino',
  'cliente@fixya.cl',
  '988888888',
  '$2y$12$89AnaEY3u/onkdv1JG2zr.meugUfo2ZtkvyguDtE4u8rJk3Q8zP5.',
  true,
  11,
  'CLIENTE'
)
ON CONFLICT (rut) DO UPDATE SET
  correo = EXCLUDED.correo,
  contrasena = EXCLUDED.contrasena,
  tipo_usuario = EXCLUDED.tipo_usuario,
  estado_usuario = EXCLUDED.estado_usuario;

-- USUARIO TÉCNICO
-- Contraseña real: tecnico123
INSERT INTO usuario (
  rut,
  nombre_completo,
  fecha_nacimiento,
  genero,
  correo,
  telefono,
  contrasena,
  estado_usuario,
  comuna_id_comuna,
  tipo_usuario
)
VALUES (
  '12311111-1',
  'Técnico Demo',
  '1995-02-15',
  'Masculino',
  'tecnico@fixya.cl',
  '977777777',
  '$2y$12$7MKIL5rQJ8sekD8SZrfQZ.zNnxsVRjkswP0G49986PzfB9dZl9CfG',
  true,
  11,
  'TECNICO'
)
ON CONFLICT (rut) DO UPDATE SET
  correo = EXCLUDED.correo,
  contrasena = EXCLUDED.contrasena,
  tipo_usuario = EXCLUDED.tipo_usuario,
  estado_usuario = EXCLUDED.estado_usuario;

-- TÉCNICO
INSERT INTO tecnico (
  usuario_rut,
  descripcion_perfil,
  experiencia_anios,
  nivel_tecnico,
  tecnico_verificado
)
VALUES (
  '12311111-1',
  'Especialista en instalaciones eléctricas',
  5,
  'Senior',
  true
)
ON CONFLICT (usuario_rut) DO NOTHING;

-- TÉCNICO SERVICIO
INSERT INTO tecnico_servicio (
  tecnico_usuario_rut,
  servicio_id_servicio
)
VALUES (
  '12311111-1',
  1
)
ON CONFLICT DO NOTHING;

-- TÉCNICO COMUNA
INSERT INTO tecnico_comuna (
  tecnico_usuario_rut,
  comuna_id_comuna
)
VALUES (
  '12311111-1',
  11
)
ON CONFLICT DO NOTHING;
