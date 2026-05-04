# 📊 Guía de Métricas Avanzadas y Visualizaciones

## 🎯 ¿Qué se agregó?

Tu aplicación ahora tiene **tres secciones principales** en el dashboard, accesibles mediante pestañas:

### 1. **Datos Básicos** 📋
Tabla original con la información estadística básica de jugadores:
- Partidos Jugados (PJ)
- Canastas Tiradas (CT)
- Canastas Encestadas (Enc.)
- Tiros de 3 Puntos (3P)

---

### 2. **Métricas Avanzadas** 📈
Las métricas que realmente muestran quiénes son los mejores jugadores:

#### **TC% (Porcentaje de Tiro de Campo)**
- Fórmula: `(Encestadas / Canastas Tiradas) × 100`
- **¿Qué significa?** Muestra la eficiencia general. Un jugador que mete 5 de 10 es más eficiente (50%) que uno que mete 8 de 20 (40%).
- **Colores:**
  - 🔴 **Rojo** (< 40%): Poco eficiente
  - 🟡 **Amarillo** (40-50%): Eficiencia media
  - 🟢 **Verde** (> 50%): Muy eficiente

#### **2P% (Porcentaje de 2 Puntos)**
- Fórmula: `(Tiros de 2 / Canastas Tiradas - 3P) × 100`
- **¿Qué significa?** Eficiencia específica en tiros de 2 puntos (sin contar triples).
- Útil para comparar a jugadores que juegan diferentes posiciones.

#### **PPP (Puntos por Partido)**
- Fórmula: `(Tiros 2P × 2 + 3P × 3) / Partidos Jugados`
- **¿Qué significa?** Promedio de puntos que anota un jugador por partido (estimado sin tiros libres).
- Este es el valor más importante para comparar ofensiva.
- Ejemplo: Si un jugador anota 25 PPP es mucho mejor que uno que anota 15 PPP.

#### **Vol. Tiro/Partido (Volumen de Tiro)**
- Fórmula: `Canastas Tiradas / Partidos Jugados`
- **¿Qué significa?** Cuántos tiros intenta un jugador por promedio.
- Indica la "dependencia ofensiva" del equipo sobre ese jugador.
- Un volumen alto (>15) significa que el equipo depende mucho de él.

---

### 3. **Gráficos** 📊
Dos visualizaciones interactivas:

#### **Scatter Plot: Volumen vs Eficiencia**
```
Eje Y: Porcentaje de Acierto (TC%)
Eje X: Canastas Tiradas
```

**Cómo interpretarlo:**
- 🌟 **Arriba-Derecha (Estrellas Eficientes)**: Tiran mucho Y aciertan mucho. Estos son los jugadores clave.
- 🔥 **Abajo-Derecha (Agujeros Negros)**: Tiran mucho pero fallan mucho. Necesitan mejorar su eficiencia.
- ✨ **Arriba-Izquierda (Eficientes de bajo volumen)**: Aciertan mucho pero no disparan mucho.
- 📉 **Abajo-Izquierda (Malos tiradores)**: Ni tiran mucho ni aciertan mucho.

Las líneas rojas y azules muestran el promedio de eficiencia y volumen.

#### **Gráfico de Barras: Rendimiento por Equipo**
```
Eje X: Puntos Totales Estimados
Cada Barra: Un equipo
```

**Cómo interpretarlo:**
- Las barras más largas = equipos con mejor rendimiento ofensivo.
- El color va de rojo (bajo) a verde (alto).
- Muestra los top 20 equipos de la temporada.
- Es la suma de todos los puntos estimados de los jugadores del equipo.

---

## 🚀 Cómo Usar

1. **Abre el Dashboard** → `/dashboard`
2. **Selecciona un Año** en el selector de la parte superior
3. **Navega entre las 3 pestañas:**
   - 📋 **Datos Básicos**: Ve la tabla original
   - 📈 **Métricas Avanzadas**: Descubre las estadísticas avanzadas
   - 📊 **Gráficos**: Haz clic en "Generar Gráficos" para ver las visualizaciones

---

## 💡 Casos de Uso

### Ejemplo 1: Encontrar la Estrella del Equipo
1. Ve a **Métricas Avanzadas**
2. Ordena mentalmente por **PPP** descendente
3. Busca un jugador con PPP alto Y TC% alto (en verde)
4. Ese es tu estrella eficiente

### Ejemplo 2: Identificar Problemas Ofensivos
1. Ve a **Gráficos**
2. Mira el **Scatter Plot**
3. Si ves muchos puntos en la zona "abajo-derecha", tu equipo está tirando mucho pero fallando
4. Necesitan mejorar la selección de tiros o el entrenamiento

### Ejemplo 3: Comparar Equipos
1. Ve a **Gráficos**
2. Mira el **Gráfico de Barras**
3. Los equipos con barras largas tienen mejor ofensiva
4. Si tu equipo está en el top 5, tienes una ofensiva muy fuerte

---

## 📊 Datos Técnicos

### APIs disponibles:

```
GET /api/datos-jugadores?ano=2023&pagina=1&items_por_pagina=20
GET /api/metricas-avanzadas?ano=2023&pagina=1&items_por_pagina=50
GET /api/generar-graficos?ano=2023
```

### Archivos modificados:
- `src/analytics.py` - Nuevas funciones de cálculo y gráficos
- `src/main.py` - Nuevos endpoints API
- `src/templates/dashboard.html` - Interfaz mejorada con pestañas

---

## ⚠️ Notas Importantes

1. **PPP es estimado**: No incluye tiros libres. Para ser exacto necesitarías esos datos.
2. **Los gráficos se generan bajo demanda**: Haz clic en "Generar Gráficos" para crearlos.
3. **Performance**: Con muchos jugadores, los gráficos pueden tardar unos segundos.
4. **Caché**: Los datos se cargan en caché la primera vez, después son muy rápidos.

---

## 🎨 Mejoras Futuras

Podrías agregar:
- Filtro por equipo en métricas avanzadas
- Comparación entre jugadores
- Histórico de temporadas (gráfico de tendencias)
- Exportar datos a Excel
- Ranking por cada métrica
