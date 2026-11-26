# language: es
Característica: El perfil público no muestra publicaciones anónimas
  Como estudiante que publica de forma anónima
  Quiero que mis publicaciones anónimas no aparezcan en mi perfil público
  Para que nadie pueda saber que yo las escribí

  # Referencia: Issue #24.

  Antecedentes:
    Dado que una estudiante tiene una publicación con su nombre y otra anónima

  Escenario: Otro usuario visita su perfil
    Cuando otro usuario entra a su perfil público
    Entonces ve la publicación con su nombre
    Y no ve la publicación anónima
    Y el contador de posts no cuenta la publicación anónima

  Escenario: La autora visita su propio perfil
    Cuando la autora entra a su perfil
    Entonces ve sus dos publicaciones, también la anónima
