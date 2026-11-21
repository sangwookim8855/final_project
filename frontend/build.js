// Vercel 빌드 명령: node build.js
// 환경 변수 API_BASE_URL(백엔드 Render 주소)을 읽어 dist/config.js를 만듭니다.
const fs = require("fs");
const path = require("path");

const apiBase = (process.env.API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const out = path.join(__dirname, "dist");

fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out);

for (const file of ["index.html", "style.css", "app.js"]) {
  fs.copyFileSync(path.join(__dirname, file), path.join(out, file));
}
fs.writeFileSync(
  path.join(out, "config.js"),
  `window.APP_CONFIG = { API_BASE_URL: ${JSON.stringify(apiBase)} };\n`
);
console.log("build done, API_BASE_URL =", apiBase);
