import api from './auth'

// 获取任务列表
export function getJobs(params) {
  return api.get('/jobs/', { params })
}

// 获取任务详情
export function getJobDetail(id) {
  return api.get(`/jobs/${id}/`)
}

// 查询任务状态
export function queryJobStatus(jobId) {
  return api.get('/jobs/query/', { params: { job_id: jobId } })
}

export default {
  getJobs,
  getJobDetail,
  queryJobStatus,
}