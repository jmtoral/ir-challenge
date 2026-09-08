/**
 * IMAGE RECOGNITION: THE GAME — Cloudflare Worker para Leaderboard Global
 * 
 * Endpoints:
 * - GET  /api/leaderboard -> Devuelve el Top 10 global ordenado por Puntos y Precisión.
 * - POST /api/score       -> Registra un nuevo puntaje de auditoría, actualiza Cloudflare KV y retorna Top 10.
 * - POST /api/reset       -> (Admin) Reinicia los puntajes con clave secreta.
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, DELETE',
  'Access-Control-Allow-Headers': 'Content-Type, Accept, X-Admin-Secret',
  'Access-Control-Max-Age': '86400',
  'Content-Type': 'application/json;charset=UTF-8'
};

// Fallback en memoria en caso de que el worker se despliegue sin KV
let inMemoryLeaderboard = [
  { nombre: 'Master Auditor', puntos: 1950, precision: 100, recall: 100, accuracy: 100, rango: 'Human Vision Engine', fecha: '2026-09-01' },
  { nombre: 'Cyber Spotter', puntos: 1720, precision: 95.0, recall: 90.0, accuracy: 88.5, rango: 'Vision Operator', fecha: '2026-09-02' },
  { nombre: 'Tiendita Pro', puntos: 1480, precision: 88.0, recall: 85.0, accuracy: 80.0, rango: 'Sharp Observer', fecha: '2026-09-03' }
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Manejo de Preflight CORS (OPTIONS)
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    // Ruta: GET /api/leaderboard o GET /
    if (request.method === 'GET' && (url.pathname === '/api/leaderboard' || url.pathname === '/')) {
      const top = await getLeaderboard(env);
      return new Response(JSON.stringify(top), { status: 200, headers: CORS_HEADERS });
    }

    // Ruta: DELETE /api/leaderboard o POST /api/reset (Protegido por clave de administrador)
    if ((request.method === 'DELETE' && url.pathname === '/api/leaderboard') || (request.method === 'POST' && url.pathname === '/api/reset')) {
      const secret = request.headers.get('X-Admin-Secret') || url.searchParams.get('admin_key');
      const expectedSecret = (env && env.ADMIN_SECRET) || 'jmtoral_ir_admin_2026';
      if (!secret || secret !== expectedSecret) {
        return new Response(JSON.stringify({ error: 'No autorizado. Se requiere clave de administrador.' }), {
          status: 403,
          headers: CORS_HEADERS
        });
      }
      await saveLeaderboard(env, []);
      return new Response(JSON.stringify({ success: true, message: 'Leaderboard reiniciado correctamente.' }), {
        status: 200,
        headers: CORS_HEADERS
      });
    }

    // Ruta: POST /api/score
    if (request.method === 'POST' && url.pathname === '/api/score') {
      try {
        const body = await request.json();

        // Validación básica
        if (!body || typeof body.nombre !== 'string' || typeof body.puntos !== 'number') {
          return new Response(JSON.stringify({ error: 'Payload inválido. Se requieren nombre (string) y puntos (number).' }), {
            status: 400,
            headers: CORS_HEADERS
          });
        }

        const nuevaEntrada = {
          nombre: String(body.nombre).slice(0, 24).trim() || 'Auditor Anónimo',
          puntos: Math.max(0, Math.round(Number(body.puntos) || 0)),
          precision: Math.min(100, Math.max(0, parseFloat((Number(body.precision) || 0).toFixed(1)))),
          recall: Math.min(100, Math.max(0, parseFloat((Number(body.recall) || 0).toFixed(1)))),
          accuracy: Math.min(100, Math.max(0, parseFloat((Number(body.accuracy) || 0).toFixed(1)))),
          rango: String(body.rango || 'Shelf Scanner').slice(0, 30),
          fecha: String(body.fecha || new Date().toISOString().slice(0, 10))
        };

        const rankingActual = await getLeaderboard(env, 50);
        rankingActual.push(nuevaEntrada);

        // Ordenar por Puntos desc, luego Precision desc, luego Recall desc
        rankingActual.sort((a, b) => {
          if ((b.puntos || 0) !== (a.puntos || 0)) {
            return (b.puntos || 0) - (a.puntos || 0);
          }
          if ((b.precision || 0) !== (a.precision || 0)) {
            return (b.precision || 0) - (a.precision || 0);
          }
          return (b.recall || 0) - (a.recall || 0);
        });

        // Guardar Top 50 en KV
        const top50 = rankingActual.slice(0, 50);
        await saveLeaderboard(env, top50);

        // Devolver Top 10 actualizado
        const top10 = top50.slice(0, 10);
        return new Response(JSON.stringify(top10), { status: 200, headers: CORS_HEADERS });
      } catch (err) {
        return new Response(JSON.stringify({ error: 'Error procesando solicitud', details: err.message }), {
          status: 500,
          headers: CORS_HEADERS
        });
      }
    }

    return new Response(JSON.stringify({ error: 'Ruta no encontrada' }), {
      status: 404,
      headers: CORS_HEADERS
    });
  }
};

async function getLeaderboard(env, limit = 10) {
  if (env && env.LEADERBOARD_KV) {
    try {
      const data = await env.LEADERBOARD_KV.get('global_leaderboard', 'json');
      if (Array.isArray(data)) return data.slice(0, limit);
    } catch (e) {
      console.error('Error leyendo de Cloudflare KV:', e);
    }
  }
  return inMemoryLeaderboard.slice(0, limit);
}

async function saveLeaderboard(env, data) {
  if (env && env.LEADERBOARD_KV) {
    try {
      await env.LEADERBOARD_KV.put('global_leaderboard', JSON.stringify(data));
      return;
    } catch (e) {
      console.error('Error escribiendo en Cloudflare KV:', e);
    }
  }
  inMemoryLeaderboard = data;
}
