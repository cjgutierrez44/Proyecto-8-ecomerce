import boto3

# Configuración de las credenciales de AWS
# Puedes establecer las credenciales de varias formas, como variables de entorno, archivos de configuración, etc.
# Aquí se utiliza la configuración por defecto.
session = boto3.Session()

# Crear una instancia del cliente de S3
s3 = session.client('s3')

# Nombre del bucket de destino
bucket_name = 'tigecomerces3'

# Ruta local de la imagen que deseas subir
local_image_path = './imagen.jpg'

# Nombre que le asignarás a la imagen en S3
s3_image_name = 'imagen.jpg'

# Subir la imagen al bucket de S3
s3.upload_file(local_image_path, bucket_name, s3_image_name)

# Imprimir mensaje de éxito
print(f"La imagen '{s3_image_name}' se ha subido correctamente al bucket '{bucket_name}' en S3.")
