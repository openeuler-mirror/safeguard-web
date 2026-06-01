/** Safeguard API */
import api from '../index'

export function getSafeguards(params) {
  return api.get('/safeguards/', { params })
}

export function getSafeguard(id) {
  return api.get(`/safeguards/${id}/`)
}

export function createSafeguard(data) {
  return api.post('/safeguards/', data)
}

export function updateSafeguard(id, data) {
  return api.put(`/safeguards/${id}/`, data)
}

export function deleteSafeguard(id) {
  return api.delete(`/safeguards/${id}/`)
}

export function deploySafeguard(id) {
  return api.post(`/safeguards/${id}/deploy/`)
}

export function rollbackSafeguard(id) {
  return api.post(`/safeguards/${id}/rollback/`)
}

export function getSafeguardStatus(id) {
  return api.get(`/safeguards/${id}/status/`)
}

export default {
  getSafeguards,
  getSafeguard,
  createSafeguard,
  updateSafeguard,
  deleteSafeguard,
  deploySafeguard,
  rollbackSafeguard,
  getSafeguardStatus,
}