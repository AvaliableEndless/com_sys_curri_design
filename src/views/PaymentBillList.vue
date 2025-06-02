<template>
  <base-list
    title="缴费管理"
    :data="paymentList"
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
      <el-form-item label="业主编号">
        <el-input v-model="searchForm.ownerNumber" placeholder="请输入业主编号" clearable />
      </el-form-item>
      <el-form-item label="房屋编号">
        <el-input v-model="searchForm.houseNumber" placeholder="请输入房屋编号" clearable />
      </el-form-item>
    </template>

    <!-- 表格列插槽 -->
    <el-table-column prop="id" label="缴费单号" width="120" />
    <el-table-column prop="owner_id" label="业主编号" width="120" />
    <el-table-column prop="house_id" label="房屋编号" width="120" />
    <el-table-column prop="type" label="缴费类型" width="120" />
    <el-table-column prop="amount" label="金额" width="120">
      <template #default="scope">
        {{ scope.row.amount }} 元
      </template>
    </el-table-column>
    <el-table-column prop="status" label="状态" width="100">
      <template #default="scope">
        <el-tag :type="scope.row.status === '已缴费' ? 'success' : 'warning'">
          {{ scope.row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="pay_way" label="缴费方式" width="120" />
  </base-list>

  <!-- 添加/编辑对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="dialogType === 'add' ? '添加缴费单' : '编辑缴费单'"
    width="500px"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="业主" prop="owner_id">
        <el-select
          v-model="form.owner_id"
          filterable
          placeholder="请选择业主"
          style="width: 100%"
          @change="handleOwnerChange"
        >
          <el-option
            v-for="owner in ownerOptions"
            :key="owner.number"
            :label="owner.name"
            :value="owner.number"
          >
            <span>{{ owner.name }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              {{ owner.number }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="房屋" prop="house_id">
        <el-select
          v-model="form.house_id"
          filterable
          placeholder="请选择房屋"
          style="width: 100%"
        >
          <el-option
            v-for="house in houseOptions"
            :key="house.number"
            :label="house.number"
            :value="house.number"
          >
            <span>{{ house.number }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              {{ house.house_type }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="缴费类型" prop="type">
        <el-select v-model="form.type" placeholder="请选择缴费类型">
          <el-option label="物业费" value="物业费" />
          <el-option label="水费" value="水费" />
          <el-option label="电费" value="电费" />
          <el-option label="燃气费" value="燃气费" />
          <el-option label="停车费" value="停车费" />
        </el-select>
      </el-form-item>
      <el-form-item label="金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :min="0"
          :precision="2"
          :step="100"
        />
      </el-form-item>
      <el-form-item label="缴费方式" prop="pay_way">
        <el-select v-model="form.pay_way" placeholder="请选择缴费方式">
          <el-option label="现金" value="现金" />
          <el-option label="微信" value="微信" />
          <el-option label="支付宝" value="支付宝" />
          <el-option label="银行卡" value="银行卡" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { paymentAPI, ownerAPI, houseAPI } from '@/api'
import BaseList from '../components/BaseList.vue'

const paymentList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref(null)
const ownerOptions = ref([])
const houseOptions = ref([])

const searchForm = reactive({
  ownerNumber: '',
  houseNumber: ''
})

const form = reactive({
  id: null,
  owner_id: '',
  house_id: '',
  type: '',
  amount: 0,
  pay_way: '现金'
})

const rules = {
  owner_id: [
    { required: true, message: '请选择业主', trigger: 'change' }
  ],
  house_id: [
    { required: true, message: '请选择房屋', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择缴费类型', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' }
  ],
  pay_way: [
    { required: true, message: '请选择缴费方式', trigger: 'change' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await paymentAPI.getList({
      page: currentPage.value,
      size: pageSize.value,
      ownerNumber: searchForm.ownerNumber || undefined,
      houseNumber: searchForm.houseNumber || undefined
    })
    if (res.code === 200) {
      paymentList.value = res.data
      total.value = res.total
    } else {
      ElMessage.error(res.message || '获取缴费单列表失败')
    }
  } catch (error) {
    console.error('获取缴费单列表失败:', error)
    ElMessage.error(error.response?.data?.message || '获取缴费单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOwnerOptions = async () => {
  try {
    const res = await ownerAPI.getList({
      page: 1,
      size: 1000
    })
    ownerOptions.value = res.data
  } catch (error) {
    ElMessage.error('获取业主列表失败')
  }
}

const fetchHouseOptions = async () => {
  try {
    const res = await houseAPI.getList({
      page: 1,
      size: 1000
    })
    houseOptions.value = res.data
  } catch (error) {
    ElMessage.error('获取房屋列表失败')
  }
}

const handleOwnerChange = (ownerNumber) => {
  const owner = ownerOptions.value.find(o => o.number === ownerNumber)
  if (owner && owner.houses) {
    houseOptions.value = owner.houses
  }
  form.house_id = ''
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
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
  form.id = null
  form.owner_id = ''
  form.house_id = ''
  form.type = ''
  form.amount = 0
  form.pay_way = '现金'
}

const handleAdd = () => {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
}

const handlePay = (row) => {
  ElMessageBox.confirm('确认进行缴费操作吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await paymentAPI.pay(row.id)
      ElMessage.success('缴费成功')
      fetchData()
    } catch (error) {
      ElMessage.error('缴费失败')
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该缴费单吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await paymentAPI.delete(row.id)
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
        const data = {
          owner_id: form.owner_id,
          house_id: form.house_id,
          type: form.type,
          amount: form.amount,
          pay_way: form.pay_way,
          status: '未缴费'
        }
        if (dialogType.value === 'add') {
          await paymentAPI.add(data)
          ElMessage.success('添加成功')
        } else {
          await paymentAPI.update(form.id, data)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '添加失败' : '更新失败')
      }
    }
  })
}

const handleReset = () => {
  searchForm.ownerNumber = ''
  searchForm.houseNumber = ''
  currentPage.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
  fetchOwnerOptions()
  fetchHouseOptions()
})
</script>

<style scoped>
.payment-list {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 