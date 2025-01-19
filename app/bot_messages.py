messages = {
"authorized_prompt" : """
Para obtener los enlaces de los grupos, utiliza los siguientes comandos: \n

- /primero : acceso a los enlaces de los grupos del primer curso \n
- /segundo : acceso a los enlaces de los grupos del segundo curso \n
- /tercero : acceso a los enlaces de los grupos del tercer curso \n
- /cuarto : acceso a los enlaces de los grupos del cuarto curso \n
"""
}

def get_email_body(code):
    email_body =   """
    Hola, \n
    Aquí tienes tu código de verificación: \n
    %s \n
    Ten en cuenta que solo es válido durante 15 minutos. \n
    """ % (code)

    return email_body