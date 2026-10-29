
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:5000'

const seccion = ref<'pacientes' | 'citas'>('pacientes')
const pacientes = ref<any[]>([])
const citas = ref<any[]>([])
const cargando = ref(false)
const mensaje = ref('')
const error = ref('')

const pacienteVacio = () => ({
  DNI: '',
  NOMBRE: '',
  APELLIDO: '',
  FECHA_DE_NACIMIENTO: '',
  CELULAR: ''
})

const citaVacia = () => ({
  ID_PACIENTE: '',
  FECHA: '',
  HORA: '',
  PRE_DIAGNOSTICO: '',
  ESTADO: 'en espera'
})

const formularioPaciente = ref<any>(pacienteVacio())
const formularioCita = ref<any>(citaVacia())
const editarPacienteId = ref<number | null>(null)
const editarCitaId = ref<number | null>(null)

function mostrarError(e: any) {
  error.value =
    e.response?.data?.error ||
    e.response?.data?.mensaje ||
    e.message ||
    'Ocurrió un error.'
}

async function cargarPacientes() {
  const respuesta = await axios.get(`${API}/pacientes`)
  pacientes.value = Array.isArray(respuesta.data)
    ? respuesta.data
    : respuesta.data.pacientes || []
}

async function cargarCitas() {
  const respuesta = await axios.get(`${API}/citas`)
  citas.value = Array.isArray(respuesta.data)
    ? respuesta.data
    : respuesta.data.citas || []
}

async function actualizarDatos() {
  cargando.value = true
  error.value = ''

  try {
    await Promise.all([cargarPacientes(), cargarCitas()])
  } catch (e: any) {
    mostrarError(e)
  } finally {
    cargando.value = false
  }
}

async function guardarPaciente() {
  error.value = ''
  mensaje.value = ''

  try {
    if (editarPacienteId.value !== null) {
      await axios.put(
        `${API}/pacientes/${editarPacienteId.value}`,
        formularioPaciente.value
      )
      mensaje.value = 'Paciente actualizado correctamente.'
    } else {
      await axios.post(`${API}/pacientes`, formularioPaciente.value)
      mensaje.value = 'Paciente registrado correctamente.'
    }

    formularioPaciente.value = pacienteVacio()
    editarPacienteId.value = null
    await actualizarDatos()
  } catch (e: any) {
    mostrarError(e)
  }
}

function prepararEdicionPaciente(p: any) {
  editarPacienteId.value = p.ID

  formularioPaciente.value = {
    DNI: p.DNI ?? '',
    NOMBRE: p.NOMBRE ?? '',
    APELLIDO: p.APELLIDO ?? '',
    FECHA_DE_NACIMIENTO: String(
      p.FECHA_DE_NACIMIENTO ?? ''
    ).slice(0, 10),
    CELULAR: p.CELULAR ?? ''
  }

  seccion.value = 'pacientes'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function eliminarPaciente(id: number) {
  if (!confirm('¿Seguro que deseas eliminar este paciente?')) return

  error.value = ''
  mensaje.value = ''

  try {
    await axios.delete(`${API}/pacientes/${id}`)
    mensaje.value = 'Paciente eliminado.'
    await actualizarDatos()
  } catch (e: any) {
    mostrarError(e)
  }
}

async function guardarCita() {
  error.value = ''
  mensaje.value = ''

  try {
    const datos = {
      ...formularioCita.value,
      ID_PACIENTE: Number(formularioCita.value.ID_PACIENTE)
    }

    if (editarCitaId.value !== null) {
      await axios.put(`${API}/citas/${editarCitaId.value}`, datos)
      mensaje.value = 'Cita actualizada correctamente.'
    } else {
      await axios.post(`${API}/citas`, datos)
      mensaje.value = 'Cita registrada correctamente.'
    }

    formularioCita.value = citaVacia()
    editarCitaId.value = null
    await actualizarDatos()
  } catch (e: any) {
    mostrarError(e)
  }
}

function prepararEdicionCita(c: any) {
  editarCitaId.value = c.ID

  formularioCita.value = {
    ID_PACIENTE: c.ID_PACIENTE ?? '',
    FECHA: String(c.FECHA ?? '').slice(0, 10),
    HORA: String(c.HORA ?? '').slice(0, 5),
    PRE_DIAGNOSTICO: c.PRE_DIAGNOSTICO ?? '',
    ESTADO: c.ESTADO ?? 'en espera'
  }

  seccion.value = 'citas'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function eliminarCita(id: number) {
  if (!confirm('¿Seguro que deseas eliminar esta cita?')) return

  error.value = ''
  mensaje.value = ''

  try {
    await axios.delete(`${API}/citas/${id}`)
    mensaje.value = 'Cita eliminada.'
    await actualizarDatos()
  } catch (e: any) {
    mostrarError(e)
  }
}

function nombrePaciente(id: number) {
  const p = pacientes.value.find(
    x => Number(x.ID) === Number(id)
  )

  return p
    ? `${p.NOMBRE} ${p.APELLIDO}`
    : `Paciente #${id}`
}

onMounted(actualizarDatos)
</script>

<template>
  <div class="aplicacion">
    <header class="encabezado">
      <div class="marca">
        <div class="logo">✚</div>
        <div>
          <h1>Consultorio Médico</h1>
          <p>Sistema de administración</p>
        </div>
      </div>

      <span class="estado">
        <span></span>
        Sistema local
      </span>
    </header>

    <main class="contenido">
      <section class="bienvenida">
        <div>
          <p class="sobretitulo">PANEL DE CONTROL</p>
          <h2>Gestión del consultorio</h2>
          <p>
            Administra los pacientes y sus citas médicas desde un solo lugar.
          </p>
        </div>

        <button class="boton-secundario" @click="actualizarDatos">
          ↻ Actualizar datos
        </button>
      </section>

      <section class="resumen">
        <article class="tarjeta-resumen">
          <div class="icono azul">♙</div>
          <div>
            <p>Pacientes registrados</p>
            <strong>{{ pacientes.length }}</strong>
          </div>
        </article>

        <article class="tarjeta-resumen">
          <div class="icono verde">▣</div>
          <div>
            <p>Citas registradas</p>
            <strong>{{ citas.length }}</strong>
          </div>
        </article>
      </section>

      <div class="pestanas">
        <button
          :class="{ activa: seccion === 'pacientes' }"
          @click="seccion = 'pacientes'"
        >
          ♙ Pacientes
        </button>

        <button
          :class="{ activa: seccion === 'citas' }"
          @click="seccion = 'citas'"
        >
          ▣ Citas médicas
        </button>
      </div>

      <div v-if="mensaje" class="aviso exito">
        {{ mensaje }}
      </div>

      <div v-if="error" class="aviso fallo">
        {{ error }}
        <p>Comprueba que Flask esté activo y permita solicitudes desde Vue.</p>
      </div>

      <p v-if="cargando" class="cargando">
        Cargando información...
      </p>

      <template v-if="seccion === 'pacientes'">
        <section class="panel">
          <div class="titulo-panel">
            <div>
              <h3>
                {{
                  editarPacienteId !== null
                    ? 'Editar paciente'
                    : 'Registrar paciente'
                }}
              </h3>
              <p>Completa los datos personales del paciente.</p>
            </div>
          </div>

          <form class="formulario" @submit.prevent="guardarPaciente">
            <label>
              DNI
              <input
                v-model.trim="formularioPaciente.DNI"
                required
                maxlength="8"
              />
            </label>

            <label>
              Nombres
              <input v-model.trim="formularioPaciente.NOMBRE" required />
            </label>

            <label>
              Apellidos
              <input v-model.trim="formularioPaciente.APELLIDO" required />
            </label>

            <label>
              Fecha de nacimiento
              <input
                v-model="formularioPaciente.FECHA_DE_NACIMIENTO"
                type="date"
                required
              />
            </label>

            <label>
              Celular
              <input v-model.trim="formularioPaciente.CELULAR" required />
            </label>

            <div class="acciones-formulario">
              <button class="boton-principal" type="submit">
                {{
                  editarPacienteId !== null
                    ? 'Guardar cambios'
                    : '+ Registrar paciente'
                }}
              </button>

              <button
                v-if="editarPacienteId !== null"
                type="button"
                class="boton-secundario"
                @click="
                  formularioPaciente = pacienteVacio();
                  editarPacienteId = null
                "
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>

        <section class="panel">
          <div class="titulo-panel">
            <div>
              <h3>Lista de pacientes</h3>
              <p>{{ pacientes.length }} registro(s)</p>
            </div>
          </div>

          <div class="tabla-contenedor">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>DNI</th>
                  <th>Nombres</th>
                  <th>Apellidos</th>
                  <th>Nacimiento</th>
                  <th>Celular</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="p in pacientes" :key="p.ID">
                  <td>{{ p.ID }}</td>
                  <td>{{ p.DNI }}</td>
                  <td>{{ p.NOMBRE }}</td>
                  <td>{{ p.APELLIDO }}</td>
                  <td>{{ p.FECHA_DE_NACIMIENTO }}</td>
                  <td>{{ p.CELULAR }}</td>

                  <td class="acciones">
                    <button
                      class="editar"
                      @click="prepararEdicionPaciente(p)"
                    >
                      Editar
                    </button>

                    <button
                      class="eliminar"
                      @click="eliminarPaciente(p.ID)"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>

                <tr v-if="!pacientes.length">
                  <td colspan="7" class="vacio">
                    No hay pacientes para mostrar.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <template v-else>
        <section class="panel">
          <div class="titulo-panel">
            <div>
              <h3>
                {{
                  editarCitaId !== null
                    ? 'Editar cita'
                    : 'Registrar cita médica'
                }}
              </h3>
              <p>Programa y actualiza las citas del consultorio.</p>
            </div>
          </div>

          <form class="formulario" @submit.prevent="guardarCita">
            <label class="campo-ancho">
              Paciente
              <select v-model="formularioCita.ID_PACIENTE" required>
                <option value="" disabled>Selecciona un paciente</option>
                <option
                  v-for="p in pacientes"
                  :key="p.ID"
                  :value="p.ID"
                >
                  {{ p.NOMBRE }} {{ p.APELLIDO }} — DNI {{ p.DNI }}
                </option>
              </select>
            </label>

            <label>
              Fecha
              <input
                v-model="formularioCita.FECHA"
                type="date"
                required
              />
            </label>

            <label>
              Hora
              <input
                v-model="formularioCita.HORA"
                type="time"
                required
              />
            </label>

            <label class="campo-ancho">
              Pre-diagnóstico
              <input
                v-model.trim="formularioCita.PRE_DIAGNOSTICO"
                required
              />
            </label>

            <label>
              Estado
              <select v-model="formularioCita.ESTADO" required>
                <option value="en espera">En espera</option>
                <option value="atendido">Atendido</option>
              </select>
            </label>

            <div class="acciones-formulario">
              <button class="boton-principal" type="submit">
                {{
                  editarCitaId !== null
                    ? 'Guardar cambios'
                    : '+ Registrar cita'
                }}
              </button>

              <button
                v-if="editarCitaId !== null"
                type="button"
                class="boton-secundario"
                @click="
                  formularioCita = citaVacia();
                  editarCitaId = null
                "
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>

        <section class="panel">
          <div class="titulo-panel">
            <div>
              <h3>Lista de citas</h3>
              <p>{{ citas.length }} registro(s)</p>
            </div>
          </div>

          <div class="tabla-contenedor">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Paciente</th>
                  <th>Fecha</th>
                  <th>Hora</th>
                  <th>Pre-diagnóstico</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="c in citas" :key="c.ID">
                  <td>{{ c.ID }}</td>
                  <td>{{ nombrePaciente(c.ID_PACIENTE) }}</td>
                  <td>{{ c.FECHA }}</td>
                  <td>{{ c.HORA }}</td>
                  <td>{{ c.PRE_DIAGNOSTICO }}</td>

                  <td>
                    <span
                      class="etiqueta"
                      :class="
                        c.ESTADO === 'atendido' ? 'atendido' : 'espera'
                      "
                    >
                      {{ c.ESTADO }}
                    </span>
                  </td>

                  <td class="acciones">
                    <button
                      class="editar"
                      @click="prepararEdicionCita(c)"
                    >
                      Editar
                    </button>

                    <button
                      class="eliminar"
                      @click="eliminarCita(c.ID)"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>

                <tr v-if="!citas.length">
                  <td colspan="7" class="vacio">
                    No hay citas para mostrar.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <footer>
        Consultorio Médico · Administración de pacientes y citas
      </footer>
    </main>
  </div>
</template>

<style>
:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system,
    BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #172b4d;
  background: #f3f6fb;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  width: 100%;
  min-width: 320px;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  min-width: 320px;
  min-height: 100%;
  margin: 0;
}

body {
  min-height: 100vh;
}

button,
input,
select {
  font: inherit;
}

button {
  cursor: pointer;
}

.aplicacion {
  width: 100%;
  min-height: 100vh;
}

.encabezado {
  width: 100%;
  background: #fff;
  min-height: 82px;
  padding: 16px 3%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5eaf2;
}

.marca {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  background: #1769d2;
  color: white;
  border-radius: 12px;
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  font-size: 27px;
}

h1 {
  font-size: 20px;
  margin: 0;
}

.marca p {
  margin: 4px 0 0;
  color: #75839a;
  font-size: 13px;
}

.estado {
  color: #28865c;
  font-size: 13px;
  display: flex;
  gap: 7px;
  align-items: center;
}

.estado span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #32b77a;
}

.contenido {
  display: block;
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 34px 3%;
}

.bienvenida {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 26px;
}

.sobretitulo {
  color: #1769d2 !important;
  font-weight: 700;
  letter-spacing: 1.5px;
  font-size: 11px !important;
  margin: 0 0 9px !important;
}

.bienvenida h2 {
  font-size: clamp(24px, 3vw, 32px);
  margin: 0 0 8px;
}

.bienvenida p {
  color: #738199;
  margin: 0;
  font-size: 14px;
}

.resumen {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 26px;
}

.tarjeta-resumen {
  background: white;
  border: 1px solid #e7ecf4;
  border-radius: 14px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 3px 12px #203c6510;
}

.icono {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  font-size: 26px;
  flex-shrink: 0;
}

.azul {
  background: #e8f1ff;
  color: #1769d2;
}

.verde {
  background: #e3f8ed;
  color: #21865a;
}

.tarjeta-resumen p {
  color: #748199;
  font-size: 13px;
  margin: 0 0 7px;
}

.tarjeta-resumen strong {
  font-size: 27px;
}

.pestanas {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #dfe6f0;
  margin-bottom: 20px;
}

.pestanas button {
  background: transparent;
  border: 0;
  padding: 14px 18px;
  color: #6c7b92;
  font-weight: 600;
  border-bottom: 3px solid transparent;
}

.pestanas button.activa {
  color: #1769d2;
  border-bottom-color: #1769d2;
}

.panel {
  width: 100%;
  background: white;
  border: 1px solid #e6ebf3;
  border-radius: 14px;
  margin-bottom: 22px;
  overflow: hidden;
  box-shadow: 0 3px 12px #203c6508;
}

.titulo-panel {
  padding: 22px 24px;
  border-bottom: 1px solid #edf0f5;
}

.titulo-panel h3 {
  margin: 0 0 6px;
  font-size: 17px;
}

.titulo-panel p {
  color: #8190a5;
  margin: 0;
  font-size: 13px;
}

.formulario {
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.formulario label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  font-size: 13px;
  color: #43536b;
  font-weight: 600;
}

.formulario input,
.formulario select {
  min-width: 0;
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #d9e1ec;
  border-radius: 8px;
  background: #fff;
  color: #24364e;
  outline: none;
}

.formulario input:focus,
.formulario select:focus {
  border-color: #4287e7;
  box-shadow: 0 0 0 3px #4287e71c;
}

.campo-ancho {
  grid-column: span 2;
}

.acciones-formulario {
  display: flex;
  gap: 10px;
  align-items: end;
  flex-wrap: wrap;
}

.boton-principal,
.boton-secundario {
  padding: 11px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
}

.boton-principal {
  background: #1769d2;
  border: 1px solid #1769d2;
  color: white;
}

.boton-principal:hover {
  background: #1059b8;
}

.boton-secundario {
  background: white;
  border: 1px solid #d9e1ec;
  color: #43536b;
}

.tabla-contenedor {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
  font-size: 13px;
}

th {
  text-align: left;
  background: #f8fafd;
  color: #66758d;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .4px;
  padding: 14px 16px;
}

td {
  padding: 14px 16px;
  border-top: 1px solid #edf0f5;
}

tbody tr:hover {
  background: #fafcff;
}

.acciones {
  display: flex;
  gap: 7px;
}

.acciones button {
  border-radius: 6px;
  padding: 6px 9px;
  font-size: 12px;
  border: 1px solid;
}

.editar {
  color: #1769d2;
  background: #edf5ff;
  border-color: #d6e7ff !important;
}

.eliminar {
  color: #c43c49;
  background: #fff0f1;
  border-color: #ffd9dd !important;
}

.etiqueta {
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  text-transform: capitalize;
}

.atendido {
  color: #19764c;
  background: #e2f7ec;
}

.espera {
  color: #986500;
  background: #fff3d7;
}

.vacio {
  text-align: center;
  color: #8794a8;
  padding: 28px;
}

.aviso {
  padding: 13px 16px;
  border-radius: 8px;
  margin: 0 0 18px;
  font-size: 14px;
}

.exito {
  background: #e6f8ef;
  color: #19764c;
}

.fallo {
  background: #fff0f0;
  color: #a52c36;
}

.fallo p {
  margin-bottom: 0;
}

.cargando {
  color: #65748b;
}

footer {
  text-align: center;
  color: #8794a8;
  padding: 24px 0 8px;
  font-size: 12px;
}

@media (max-width: 1000px) {
  .formulario {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 850px) {
  .contenido {
    padding: 24px 4%;
  }
}

@media (max-width: 560px) {
  .encabezado {
    padding: 14px 4%;
  }

  .estado {
    font-size: 11px;
  }

  h1 {
    font-size: 17px;
  }

  .bienvenida {
    align-items: flex-start;
    flex-direction: column;
  }

  .resumen {
    gap: 10px;
  }

  .tarjeta-resumen {
    padding: 14px;
    gap: 10px;
  }

  .icono {
    width: 38px;
    height: 38px;
    font-size: 21px;
  }

  .tarjeta-resumen p {
    font-size: 11px;
  }

  .tarjeta-resumen strong {
    font-size: 22px;
  }

  .formulario {
    grid-template-columns: 1fr;
    padding: 18px;
  }

  .campo-ancho {
    grid-column: span 1;
  }

  .titulo-panel {
    padding: 18px;
  }

  .pestanas button {
    padding: 12px 10px;
    font-size: 13px;
  }
}
</style>
