/* Marcar como leída y eliminar notificaciones (RF-41 y RF-42). */

function enviarAccionNotificacion(ruta) {
  return fetch(ruta, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        // El sidebar escucha este evento para actualizar el contador.
        window.dispatchEvent(new CustomEvent('notificaciones:no-leidas', { detail: data.no_leidas }));
      }
      return data;
    });
}

function quitarMarcaNoLeida(tarjeta) {
  tarjeta.classList.remove('no-leida');
  const boton = tarjeta.querySelector('[data-marcar-leida]');
  if (boton) boton.remove();
}

function actualizarBotonLeerTodas() {
  const boton = document.querySelector('[data-leer-todas]');
  if (boton && !document.querySelector('.notif-card.no-leida')) boton.remove();
}

delegar('click', '[data-marcar-leida]', function (boton) {
  const tarjeta = boton.closest('[data-notificacion]');
  boton.disabled = true;
  enviarAccionNotificacion(`/notificaciones/${boton.dataset.marcarLeida}/leida`)
    .then(data => {
      if (data.ok) {
        quitarMarcaNoLeida(tarjeta);
        actualizarBotonLeerTodas();
      } else {
        boton.disabled = false;
      }
    })
    .catch(() => { boton.disabled = false; });
});

delegar('click', '[data-eliminar-notificacion]', function (boton) {
  const tarjeta = boton.closest('[data-notificacion]');
  boton.disabled = true;
  enviarAccionNotificacion(`/notificaciones/${boton.dataset.eliminarNotificacion}/eliminar`)
    .then(data => {
      // Si ya no existe (404), también la quitamos de la lista.
      tarjeta.remove();
      actualizarBotonLeerTodas();
      if (!document.querySelector('[data-notificacion]')) {
        document.getElementById('notif-vacio').hidden = false;
      }
    })
    .catch(() => { boton.disabled = false; });
});

delegar('click', '[data-leer-todas]', function (boton) {
  boton.disabled = true;
  enviarAccionNotificacion('/notificaciones/leer-todas')
    .then(data => {
      if (!data.ok) { boton.disabled = false; return; }
      document.querySelectorAll('.notif-card.no-leida').forEach(quitarMarcaNoLeida);
      boton.remove();
    })
    .catch(() => { boton.disabled = false; });
});

/* Al abrir una notificación no leída, se marca como leída antes de ir a su enlace. */
delegar('click', '[data-abrir-notificacion]', function (enlace) {
  const tarjeta = enlace.closest('[data-notificacion]');
  if (!tarjeta.classList.contains('no-leida')) return;
  fetch(`/notificaciones/${enlace.dataset.abrirNotificacion}/leida`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    keepalive: true,
  }).catch(() => {});
  quitarMarcaNoLeida(tarjeta);
});
