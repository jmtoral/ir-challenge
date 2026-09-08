# Despliegue del Leaderboard Global (Cloudflare Workers + KV)

Este servicio permite que todos los jugadores en **GitHub Pages** compartan el mismo Leaderboard Top 10 global en tiempo real, con costo $0 y sin necesidad de administrar servidores.

---

## Opción Rápida: Despliegue desde la Web de Cloudflare (Sin instalar nada, 2 minutos)

1. **Inicia sesión o regístrate gratis** en [cloudflare.com](https://dash.cloudflare.com/).
2. En el menú lateral izquierdo, ve a **Compute (Workers) > Workers & Pages > Create application > Create Worker**.
3. Nómbralo `ir-challenge-leaderboard` y haz clic en **Deploy**.
4. Haz clic en **Edit code** y reemplaza todo el contenido del editor con el código de [`worker.js`](file:///d:/PROYECTOS_PERSONALES/ir_challenge/server/worker.js).
5. Haz clic en **Save and Deploy**.
6. **(Recomendado para persistencia en base de datos permanente)**:
   - En el menú lateral ve a **Storage & Databases > KV**.
   - Haz clic en **Create Namespace**, nómbralo `LEADERBOARD_KV`.
   - Vuelve a tu Worker > pestaña **Settings > Variables > KV Namespace Bindings**.
   - Haz clic en **Add binding**:
     - Variable name = `LEADERBOARD_KV`
     - KV namespace = `LEADERBOARD_KV`
   - Haz clic en **Save and Deploy**.
7. **Copia la URL pública de tu Worker** (ejemplo: `https://ir-challenge-leaderboard.tu-usuario.workers.dev`).
8. En `game.js`, pega esa URL en `CONFIG.leaderboard.apiUrl`:
   ```javascript
   const CONFIG = {
     leaderboard: {
       maxEntries: 10,
       apiUrl: 'https://ir-challenge-leaderboard.tu-usuario.workers.dev'
     }
   };
   ```
9. ¡Listo! Al hacer `git push`, tu juego en GitHub Pages estará sincronizado en tiempo real con el Leaderboard global.

---

## Opción CLI: Usando Wrangler

```bash
cd server

# Iniciar sesión en Cloudflare
npx wrangler login

# Crear el namespace KV
npx wrangler kv:namespace create LEADERBOARD_KV

# Copia el ID que te devuelve la terminal y descoméntalo en wrangler.toml

# Desplegar a producción
npx wrangler deploy
```

---

## Endpoints de la API

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/leaderboard` | Devuelve el array JSON con el Top 10 de auditores. |
| `POST` | `/api/score` | Registra una partida y devuelve el Top 10 actualizado. |
| `POST` | `/api/reset` | Reinicia el ranking (requiere header `X-Admin-Secret: jmtoral_ir_admin_2026`). |
