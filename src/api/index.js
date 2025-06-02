import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 5000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res
    } else {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    console.error('API Error:', error.response || error)
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

  // 业主相关接口
  export const ownerAPI = {
    // 获取业主列表
    getList: (params) => {
      return api.get('/owners', { params })
    },
    // 搜索业主
    search: (query) => {
      return api.get('/owners/search', { params: { query } })
    },
    // 添加业主
    add: (data) => {
      return api.post('/owners', data)
    },
    // 更新业主信息
    update: (id, data) => {
      return api.put(`/owners/${id}`, data)
    },
    // 删除业主
    delete: (id) => {
      return api.delete(`/owners/${id}`)
    },
    // 获取业主的房屋
    getHouses: (id) => {
      return api.get(`/owners/${id}/houses`)
    }
  }

  // 房屋相关接口
  export const houseAPI = {
    // 获取房屋列表
    getList: (params) => {
      return api.get('/houses', { params })
    },
    // 搜索房屋
    search: (query) => {
      return api.get('/houses/search', { params: { query } })
    },
    // 添加房屋
    add: (data) => {
      return api.post('/houses', data)
    },
    // 更新房屋信息
    update: (id, data) => {
      return api.put(`/houses/${id}`, data)
    },
    // 删除房屋
    delete: (id) => {
      return api.delete(`/houses/${id}`)
    }
  }

  // 缴费单相关接口
  export const paymentAPI = {
    // 获取缴费单列表
    getList: (params) => {
      return api.get('/payment-bills', { params })
    },
    // 添加缴费单
    add: (data) => {
      return api.post('/payment-bills', data)
    },
    // 更新缴费单
    update: (id, data) => {
      return api.put(`/payment-bills/${id}`, data)
    },
    // 处理缴费
    pay: (id) => {
      return api.post(`/payment-bills/${id}/pay`)
    }
  }

// 违规单相关接口
export const violationAPI = {
  // 获取违规单列表
  getList: (params) => {
    return api.get('/violation-bills', { params })
  },
  // 添加违规单
  add: (data) => {
    return api.post('/violation-bills', data)
  },
  // 更新违规单
  update: (id, data) => {
    return api.put(`/violation-bills/${id}`, data)
  },
  // 处理违规
  process: (id, data) => {
    return api.post(`/violation-bills/${id}/process`, data)
  },
  // 删除违规单
  delete: (id) => {
    return api.delete(`/violation-bills/${id}`)
  }
}

// 投诉单相关接口
export const complaintAPI = {
  // 获取投诉单列表
  getList: (params) => {
    return api.get('/complaint-bills', { params })
  },
  // 添加投诉单
  add: (data) => {
    return api.post('/complaint-bills', data)
  },
  // 更新投诉单
  update: (id, data) => {
    return api.put(`/complaint-bills/${id}`, data)
  },
  // 处理投诉
  process: (id, data) => {
    return api.post(`/complaint-bills/${id}/process`, data)
  }
}

// 维修单相关接口
export const repairAPI = {
  // 获取维修单列表
  getList: (params) => {
    return api.get('/repair-bills', { params })
  },
  // 添加维修单
  add: (data) => {
    return api.post('/repair-bills', data)
  },
  // 更新维修单
  update: (id, data) => {
    return api.put(`/repair-bills/${id}`, data)
  },
  // 分配维修工
  assign: (id, data) => {
    return api.post(`/repair-bills/${id}/assign`, data)
  },
  // 完成维修
  complete: (id, data) => {
    return api.post(`/repair-bills/${id}/complete`, data)
  }
}

// 维修工相关接口
export const workerAPI = {
  // 获取维修工列表
  getList: (params) => {
    return api.get('/repair_workers', { params })
  },
  // 添加维修工
  add: (data) => {
    // 确保数据符合后端模型要求
    const workerData = {
      number: data.number,
      name: data.name,
      worktype: data.worktype,
      phone: data.phone,
      address: data.address
    }
    return api.post('/repair_workers', workerData)
  },
  // 更新维修工信息
  update: (id, data) => {
    // 确保数据符合后端模型要求
    const workerData = {
      number: data.number,
      name: data.name,
      worktype: data.worktype,
      phone: data.phone,
      address: data.address
    }
    return api.put(`/repair_workers/${id}`, workerData)
  },
  // 删除维修工
  delete: (id) => {
    return api.delete(`/repair_workers/${id}`)
  }
}

export default api 