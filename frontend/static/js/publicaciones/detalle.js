// ── Reacción AJAX (toggle sin recargar página) ──────────
async function reaccionar(postId) {
  const btn = document.getElementById('btn-reaccion');
  const total = document.getElementById('total-reacciones');

  try {
    const res = await fetch(`/reaccionar/${postId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();

    if (data.ok) {
      total.textContent = data.total;
      btn.classList.toggle('activa', data.activa);
    }
  } catch (e) {
    console.error('Error al reaccionar:', e);
  }
}

// ── Cerrar modales al hacer clic fuera o con Escape ──────
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('visible');
});

document.addEventListener('keydown', function (e) {
  if (e.key !== 'Escape') return;
  document.querySelectorAll('.modal-overlay.visible').forEach(function (m) {
    m.classList.remove('visible');
  });
});

// ── Reportar publicación (AJAX) ─────────────────────────
async function enviarReporte(form) {
  const mensaje = document.getElementById('reporte-mensaje');
  const boton = form.querySelector('button[type="submit"]');
  const cuerpo = new URLSearchParams({
    tipo: 'publicacion',
    contenido_id: form.dataset.reportarPublicacion,
    motivo: form.elements.motivo.value
  });

  boton.disabled = true;
  mensaje.className = 'reporte-mensaje';
  mensaje.textContent = '';

  try {
    const res = await fetch('/reporte/nuevo', { method: 'POST', body: cuerpo });
    const data = await res.json();

    if (data.ok) {
      mensaje.classList.add('ok');
      mensaje.textContent = 'Reporte enviado. Los moderadores lo revisarán.';
      return;  // el botón queda desactivado para no repetir el envío
    }
    mensaje.classList.add('error');
    mensaje.textContent = data.error || 'No se pudo enviar el reporte.';
  } catch (e) {
    console.error('Error al reportar:', e);
    mensaje.classList.add('error');
    mensaje.textContent = 'No se pudo conectar con el servidor.';
  }
  boton.disabled = false;
}

delegar('click', '[data-reaccionar]', function (el) {
  reaccionar(Number(el.dataset.reaccionar));
});


delegar('submit', 'form[data-reportar-publicacion]', function (form, e) {
  e.preventDefault();
  enviarReporte(form);
});
