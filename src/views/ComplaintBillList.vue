<template>
  <base-list
    title="投诉管理"
    :data="complaintList"
    :loading="loading"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :total="total"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
    @add="handleAdd"
    @search="handleSearch"
    @reset="handleReset"
  >
    <!-- 搜索表单插槽 -->
    <template #search>
      <el-form-item label="业主姓名">
        <el-input
          v-model="searchForm.ownerName"
          placeholder="请输入业主姓名"
          clearable
          @clear="handleSearch"
        />
      </el-form-item>
      <el-form-item label="房屋编号">
        <el-input
          v-model="searchForm.houseNumber"
          placeholder="请输入房屋编号"
          clearable
          @clear="handleSearch"
        />
      </el-form-item>
    </template>

    <!-- 表格列插槽 -->
    <el-table-column prop="id" label="投诉编号" width="100" />
    <el-table-column prop="owner_id" label="业主编号" width="120" />
    <el-table-column prop="owner_name" label="投诉人" width="120" />
    <el-table-column prop="house_id" label="房屋编号" width="120" />
    <el-table-column prop="content" label="投诉内容" show-overflow-tooltip />
    <el-table-column prop="complaint_date" label="投诉时间" width="180" />
    <el-table-column prop="process_result" label="处理状态" width="100">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.process_result)">
          {{ row.process_result }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="operator" label="经办人" width="100" />
    <el-table-column prop="processed_at" label="处理时间" width="180" />
    <el-table-column label="操作" width="200">
      <template #default="{ row }">
        <el-button 
          type="primary" 
          size="small" 
          @click="handleProcess(row)"
          v-if="row.process_result === '未处理'"
        >
          处理
        </el-button>
        <el-button 
          type="danger" 
          size="small" 
          @click="handleDelete(row)"
          v-if="row.process_result === '未处理'"
        >
          删除
        </el-button>
      </template>
    </el-table-column>
  </base-list>

  <!-- 添加投诉单对话框 -->
  <el-dialog
    v-model="addDialogVisible"
    title="添加投诉单"
    width="500px"
  >
    <el-form
      ref="addFormRef"
      :model="addForm"
      :rules="addRules"
      label-width="100px"
    >
      <el-form-item label="投诉人" prop="owner_id">
        <el-select
          v-model="addForm.owner_id"
          filterable
          remote
          :remote-method="searchOwners"
          placeholder="请输入业主姓名搜索"
          @change="handleOwnerChange"
        >
          <el-option
            v-for="owner in ownerOptions"
            :key="owner.id"
            :label="owner.name"
            :value="owner.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="房屋编号" prop="house_id">
        <el-select
          v-model="addForm.house_id"
          placeholder="请选择房屋"
          :disabled="!addForm.owner_id"
        >
          <el-option
            v-for="house in ownerHouses"
            :key="house.id"
            :label="house.number"
            :value="house.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="投诉内容" prop="content">
        <el-input
          v-model="addForm.content"
          type="textarea"
          :rows="3"
          placeholder="请输入投诉内容"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">确定</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 处理投诉对话框 -->
  <el-dialog
    v-model="processDialogVisible"
    title="处理投诉"
    width="500px"
  >
    <el-form
      ref="processFormRef"
      :model="processForm"
      :rules="processRules"
      label-width="100px"
    >
      <el-form-item label="处理结果" prop="process_result">
        <el-input
          v-model="processForm.process_result"
          type="textarea"
          :rows="3"
          placeholder="请输入处理结果"
        />
      </el-form-item>
      <el-form-item label="经办人" prop="operator">
        <el-input v-model="processForm.operator" placeholder="请输入经办人" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseList from '../components/BaseList.vue'
import { complaintAPI, ownerAPI, houseAPI } from '../api'

const complaintList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = ref({
  ownerName: '',
  houseNumber: ''
})

// 业主和房屋选项
const ownerOptions = ref([])
const houseOptions = ref([])

// 搜索业主
const searchOwners = async (query) => {
  if (query) {
    try {
      const res = await ownerAPI.search(query)
      ownerOptions.value = res.data.map(owner => ({
        id: owner.id,
        name: owner.name
      }))
    } catch (error) {
      console.error('搜索业主失败:', error)
      ElMessage.error('搜索业主失败')
    }
  } else {
    ownerOptions.value = []
  }
}

// 搜索房屋
const searchHouses = async (query) => {
  if (query) {
    try {
      const res = await houseAPI.search(query)
      houseOptions.value = res.data.map(house => ({
        id: house.id,
        number: house.number
      }))
    } catch (error) {
      console.error('搜索房屋失败:', error)
      ElMessage.error('搜索房屋失败')
    }
  } else {
    houseOptions.value = []
  }
}

// 添加投诉单相关
const addDialogVisible = ref(false)
const addFormRef = ref(null)
const addForm = ref({
  owner_id: '',
  house_id: '',
  content: ''
})
const addRules = {
  owner_id: [{ required: true, message: '请选择投诉人', trigger: 'change' }],
  house_id: [{ required: true, message: '请选择房屋', trigger: 'change' }],
  content: [{ required: true, message: '请输入投诉内容', trigger: 'blur' }]
}

// 处理投诉相关
const processDialogVisible = ref(false)
const processFormRef = ref(null)
const processForm = ref({
  process_result: '',
  operator: ''
})
const processRules = {
  process_result: [{ required: true, message: '请输入处理结果', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入经办人', trigger: 'blur' }]
}
const currentComplaint = ref(null)

// 业主的房屋列表
const ownerHouses = ref([])

// 处理业主选择变化
const handleOwnerChange = async (ownerId) => {
  if (!ownerId) {
    ownerHouses.value = []
    addForm.value.house_id = ''
    return
  }
  
  try {
    const res = await ownerAPI.getHouses(ownerId)
    ownerHouses.value = res.data
    // 如果业主只有一套房屋，自动选择
    if (ownerHouses.value.length === 1) {
      addForm.value.house_id = ownerHouses.value[0].id
    } else {
      addForm.value.house_id = ''
    }
  } catch (error) {
    console.error('获取业主房屋失败:', error)
    ElMessage.error('获取业主房屋失败')
    ownerHouses.value = []
    addForm.value.house_id = ''
  }
}

// 获取投诉单列表
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      ownerName: searchForm.value.ownerName,
      houseNumber: searchForm.value.houseNumber
    }
    const res = await complaintAPI.getList(params)
    if (res.code === 200) {
      complaintList.value = res.data
      total.value = res.total
    } else {
      ElMessage.error(res.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取投诉单列表失败:', error)
    ElMessage.error(error.response?.data?.message || '获取数据失败，请重试')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  searchForm.value.ownerName = ''
  searchForm.value.houseNumber = ''
  currentPage.value = 1
  fetchData()
}

// 处理分页变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

// 处理添加投诉单
const handleAdd = () => {
  addForm.value = {
    owner_id: '',
    house_id: '',
    content: ''
  }
  ownerHouses.value = []
  addDialogVisible.value = true
}

const submitAdd = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await complaintAPI.add(addForm.value)
        ElMessage.success('添加成功')
        addDialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('添加投诉单失败:', error)
        ElMessage.error('添加投诉单失败')
      }
    }
  })
}

// 处理投诉
const handleProcess = (row) => {
  currentComplaint.value = row
  processForm.value = {
    process_result: '',
    operator: ''
  }
  processDialogVisible.value = true
}

const submitProcess = async () => {
  if (!processFormRef.value || !currentComplaint.value) return
  
  await processFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await complaintAPI.process(currentComplaint.value.id, processForm.value)
        ElMessage.success('处理成功')
        processDialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('处理投诉失败:', error)
        ElMessage.error('处理投诉失败')
      }
    }
  })
}

// 删除投诉单
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该投诉单吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await complaintAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除投诉单失败:', error)
      ElMessage.error('删除投诉单失败')
    }
  }).catch(() => {})
}

// 获取状态标签类型
const getStatusType = (status) => {
  const types = {
    '未处理': 'warning',
    '已处理': 'success'
  }
  return types[status] || 'info'
}

onMounted(() => {
  fetchData()
})
</script> 