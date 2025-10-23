from django.db import models

class ContactosContacto(models.Model):
    id = models.BigAutoField(primary_key=True)
    rut_contacto = models.CharField(max_length=12)
    nombre_contacto = models.CharField(max_length=200)
    parentesco = models.CharField(max_length=100)
    tipo_contacto = models.CharField(max_length=100)
    fecha_registro = models.DateField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    estado_estudio = models.CharField(max_length=100)
    
    # CORRECCIÓN: Usar string para la referencia y especificar el app_label
    paciente_indice = models.ForeignKey(
        'pacientes.PacientesPaciente', 
        on_delete=models.CASCADE,  # Cambié de DO_NOTHING a CASCADE para mejor manejo
        db_column='paciente_indice_id'  # Especificar nombre de columna en BD
    )

    class Meta:
        managed = False  # Mantener False ya que la tabla ya existe
        db_table = 'contactos_contacto'

    def __str__(self):
        return f"{self.nombre_contacto} ({self.rut_contacto})"