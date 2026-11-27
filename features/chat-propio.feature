# language: es
Característica: Abrir el chat con mi propia cuenta
  Como estudiante
  Quiero que la aplicación no falle si intento abrir un chat conmigo mismo
  Para no ver un error y poder seguir usando los mensajes

  # Referencia: Issue #28 (RNF-07, relacionado con RF-44).

  Antecedentes:
    Dado que inicié sesión como estudiante

  Escenario: Abrir el chat con mi propio id
    Cuando entro a la dirección del chat con mi propio usuario
    Entonces vuelvo a la lista de mensajes
    Y veo el aviso "No puedes abrir un chat contigo mismo."
    Y no se crea ninguna conversación nueva

  Escenario: Ya tengo conversaciones con otras personas
    Dado que tengo un chat con otro estudiante
    Cuando entro a la dirección del chat con mi propio usuario
    Entonces no se abre el chat de la otra persona
    Y vuelvo a la lista de mensajes

  Escenario: Abrir el chat con otra persona
    Cuando abro el chat con otro estudiante
    Entonces se abre la conversación con esa persona
