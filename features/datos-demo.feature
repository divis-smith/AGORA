# language: es
Característica: Datos de demostración vigentes
  Como equipo de desarrollo
  Necesito que los eventos de demostración se creen con fechas futuras respecto al día en que se ejecuta el script
  Para que la demo y el README funcionen sin importar cuándo se cree la base

  # Referencia: Issue #29 y RNF-07 (relacionado: RF-26).

  Escenario: Eventos de demostración visibles
    Dado que creo la base con "python scripts/crear_db.py" en cualquier fecha
    Cuando inicio sesión como estudiante y abro Eventos
    Entonces veo los eventos de demostración como próximos
    Y no veo el mensaje "Sin eventos próximos"

  Escenario: El panel cuenta los eventos de demostración
    Dado que creo la base con "python scripts/crear_db.py"
    Cuando un administrador abre el panel de administración
    Entonces "Eventos próximos" muestra un número mayor que cero
