# Parametrización para añadir un nuevo tenant

---

## VAPI

1. **Tool**
   * `CheckAvailability` →  **Server URL** : configurar el webhook de **n8n** del nuevo cliente.
2. **Asistente**
   * Campo **Messaging** (al final) →  **Server URL** : configurar el webhook de **n8n** del nuevo cliente.
3. **Prompt***(a ajustar en la versión final)*
   * Nombre del asistente (x2).
   * Nombre del restaurante (x2).
   * Contexto del servicio: horarios y días de apertura.

---

## N8N

### Cambiar credenciales

* **PostgreSQL** : solo si no se reutiliza la misma base de datos.
* **Telnyx/Twilio** : necesario para configurar un nuevo número móvil.

### Nodos 1º Flujo

* **Webhook** : usar la **Production URL** para todo.
* **Conf_cliente2** : actualizar los campos  **From** , **To** y  **message** .

### Nodos 2º Flujo

* **IfTelefono:**
* **MensajeReservaCancelada**

---

## PostgreSQL

### Tablas

* **horarios_disponibles** :
  * Definir días activos y franjas horarias.
  * Intervalos de reserva: 15 min o 30 min.
* **mesas** :
  * Número de mesas, sillas, posición, interior/exterior, etc.

### Funciones (si existen)

* Revisar:
  * Borrado automático de registros.
  * Políticas de asignación de número de personas a mesas según tamaño.

---

## Proveedor móvil (Telnyx / Twilio)

* Configurar la cuenta y el número asociado al nuevo tenant.
