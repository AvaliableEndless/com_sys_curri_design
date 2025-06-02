<template>
  <base-list
    title="维修工管理"
    :data="workerList"
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
      <el-form-item label="姓名">
        <el-input 
          v-model="searchForm.name" 
          placeholder="请输入维修工姓名" 
          clearable
          @clear="handleSearch"
        />
      </el-form-item>
    </template>

    <!-- 表格列插槽 -->
    <el-table-column prop="number" label="工号" width="120" />
    <el-table-column prop="name" label="姓名" />
    <el-table-column prop="worktype" label="工种" />
    <el-table-column prop="phone" label="联系电话" />
    <el-table-column prop="address" label="地址" show-overflow-tooltip />
    <el-table-column label="操作" width="200">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
        <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
      </template>
    </el-table-column>
  </base-list>

  <!-- 添加/编辑维修工对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑维修工' : '添加维修工'"
    width="500px"
  >
    <el-form
      ref="formRef"
      :model="editData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="工号" prop="number">
        <el-input v-model="editData.number" placeholder="请输入工号" />
      </el-form-item>
      <el-form-item label="姓名" prop="name">
        <el-input v-model="editData.name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="工种" prop="worktype">
        <el-select v-model="editData.worktype" placeholder="请选择工种">
          <el-option label="水电维修" value="水电维修" />
          <el-option label="木工维修" value="木工维修" />
          <el-option label="油漆维修" value="油漆维修" />
          <el-option label="综合维修" value="综合维修" />
        </el-select>
      </el-form-item>
      <el-form-item label="联系电话" prop="phone">
        <el-input v-model="editData.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="地址" prop="address">
        <el-input v-model="editData.address" placeholder="请输入地址" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseList from '../components/BaseList.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workerAPI } from '../api'

const workerList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = ref({
  name: ''
})
const isEdit = ref(false)
const editData = ref({})
const dialogVisible = ref(false)
const formRef = ref(null)

// 表单验证规则
const rules = {
  number: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  worktype: [
    { required: true, message: '请选择工种', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入地址', trigger: 'blur' }
  ]
}

// 获取维修工列表数据
const fetchWorkerList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      name: searchForm.value.name
    }
    const res = await workerAPI.getList(params)
    if (res.code === 200) {
      workerList.value = res.data
      total.value = res.total
    } else {
      ElMessage.error(res.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取维修工列表失败:', error)
    ElMessage.error(error.response?.data?.message || '获取数据失败，请重试')
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchWorkerList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchWorkerList()
}

// 处理添加维修工
const handleAdd = () => {
  isEdit.value = false
  editData.value = {
    number: '',
    name: '',
    worktype: '',
    phone: '',
    address: ''
  }
  dialogVisible.value = true
}

// 处理编辑维修工
const handleEdit = (row) => {
  isEdit.value = true
  editData.value = { ...row }
  dialogVisible.value = true
}

// 处理删除维修工
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除维修工"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await workerAPI.delete(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchWorkerList()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败，请重试')
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let res
        if (isEdit.value) {
          res = await workerAPI.update(editData.value.id, editData.value)
        } else {
          res = await workerAPI.add(editData.value)
        }
        
        if (res.code === 200) {
          ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
          dialogVisible.value = false
          fetchWorkerList()
        } else {
          ElMessage.error(res.message || (isEdit.value ? '更新失败' : '添加失败'))
        }
      } catch (error) {
        console.error(isEdit.value ? '更新失败:' : '添加失败:', error)
        ElMessage.error(error.response?.data?.message || (isEdit.value ? '更新失败' : '添加失败'))
      }
    }
  })
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchWorkerList()
}

// 处理重置
const handleReset = () => {
  searchForm.value.name = ''
  currentPage.value = 1
  fetchWorkerList()
}

onMounted(() => {
  fetchWorkerList()
})
</script> 