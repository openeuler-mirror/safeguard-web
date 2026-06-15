import api from './auth'

export function getTasks(params) {
  return api.get('/tasks/', { params })
}

export function getTask(id) {
  return api.get(`/tasks/${id}/`)
}

export function queryTasks(data) {
  return api.post('/tasks/query/', data)
}

export function pageTasks(data, params) {
  return api.post('/tasks/page/', data, { params })
}

export default {
  getTasks,
  getTask,
  queryTasks,
  pageTasks,
}
