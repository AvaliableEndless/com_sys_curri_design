<template>
  <base-list
    title="房屋管理"
    :data="houseList"
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
      <el-form-item label="房屋编号">
        <el-input v-model="searchForm.number" placeholder="请输入房屋编号" clearable />
      </el-form-item>
    </template>

    <!-- 表格列插槽 -->
    <el-table-column prop="number" label="房屋编号" width="120" />
    <el-table-column prop="area" label="面积(㎡)" width="120" />
    <el-table-column prop="using_area" label="使用面积(㎡)" width="120" />
    <el-table-column prop="house_type" label="房型" width="120" />
    <el-table-column label="操作" width="150" fixed="right">
      <template #default="scope">
        <el-button
          type="primary"
          size="small"
          @click="handleEdit(scope.row)"
        >
          编辑
        </el-button>
        <el-button
          type="danger"
          size="small"
          @click="handleDelete(scope.row)"
        >
          删除
        </el-button>
      </template>
    </el-table-column>
  </base-list>

  <!-- 添加/编辑对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑房屋' : '添加房屋'"
    width="500px"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="房屋编号" prop="number">
        <el-input v-model="form.number" placeholder="请输入房屋编号" />
      </el-form-item>
      <el-form-item label="面积" prop="area">
        <el-input-number
          v-model="form.area"
          :min="0"
          :precision="2"
          :step="10"
        />
      </el-form-item>
      <el-form-item label="使用面积" prop="using_area">
        <el-input-number
          v-model="form.using_area"
          :min="0"
          :precision="2"
          :step="10"
        />
      </el-form-item>
      <el-form-item label="房型" prop="house_type">
        <el-select v-model="form.house_type" placeholder="请选择房型">
          <el-option label="一室一厅" value="一室一厅" />
          <el-option label="两室一厅" value="两室一厅" />
          <el-option label="三室一厅" value="三室一厅" />
          <el-option label="三室两厅" value="三室两厅" />
          <el-option label="四室两厅" value="四室两厅" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import BaseList from '../components/BaseList.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { houseAPI } from '@/api'

const houseList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  number: ''
})

const form = reactive({
  number: '',
  area: 0,
  using_area: 0,
  house_type: ''
})

const rules = {
  number: [
    { required: true, message: '请输入房屋编号', trigger: 'blur' }
  ],
  area: [
    { required: true, message: '请输入面积', trigger: 'blur' }
  ],
  using_area: [
    { required: true, message: '请输入使用面积', trigger: 'blur' }
  ],
  house_type: [
    { required: true, message: '请选择房型', trigger: 'change' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await houseAPI.getList({
      page: currentPage.value,
      size: pageSize.value,
      number: searchForm.number || undefined
    })
    if (res.code === 200) {
      houseList.value = res.data
      total.value = res.total
    } else {
      ElMessage.error(res.message || '获取房屋列表失败')
    }
  } catch (error) {
    console.error('获取房屋列表失败:', error)
    ElMessage.error(error.response?.data?.message || '获取房屋列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const resetForm = () => {
  form.number = ''
  form.area = 0
  form.using_area = 0
  form.house_type = ''
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该房屋吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await houseAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await houseAPI.update(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await houseAPI.add(form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
      }
    }
  })
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  searchForm.number = ''
  currentPage.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 