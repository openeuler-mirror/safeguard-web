import api from './auth'

export function getMigrates(params) {
  return api.get('/migrates/', { params })
}

export function getMigrate(id) {
  return api.get(`/migrates/${id}/`)
}

export function createMigrateInit(data) {
  return api.post('/migrates/init/', data)
}

export function createMigrate(data) {
  return api.post('/migrates/migrate/', data)
}

export function createMigrateBack(data) {
  return api.post('/migrates/back/', data)
}

export function getMigrateStatus(id) {
  return api.get(`/migrates/${id}/status/`)
}

export default {
  getMigrates,
  getMigrate,
  createMigrateInit,
  createMigrate,
  createMigrateBack,
  getMigrateStatus,
}
