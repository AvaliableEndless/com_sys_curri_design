<template>
  <div class="violation-list">
    <div class="search-bar">
      <el-input
        v-model="searchForm.ownerNumber"
        placeholder="业主编号"
        clearable
        @clear="handleSearch"
      />
      <el-input
        v-model="searchForm.houseNumber"
        placeholder="房屋编号"
        clearable
        @clear="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
      <el-button type="success" @click="handleAdd">添加违规记录</el-button>
    </div>

    <el-table :data="violationList" border style="width: 100%">
      <el-table-column prop="id" label="违规单号" width="120" />
      <el-table-column prop="owner_id" label="业主编号" width="120" />
      <el-table-column prop="house_id" label="房屋编号" width="120" />
      <el-table-column prop="type" label="违规描述" min-width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '已处理' ? 'success' : 'warning'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="worker" label="处理人员" width="120" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button
            v-if="scope.row.status === '未处理'"
            type="primary"
            size="small"
            @click="handleProcess(scope.row)"
          >
            处理
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
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />

    <el-dialog
      v-model="processDialogVisible"
      title="处理违规"
      width="500px"
    >
      <el-form
        ref="processFormRef"
        :model="processForm"
        :rules="processRules"
        label-width="100px"
      >
        <el-form-item label="处理结果" prop="result">
          <el-input
            v-model="processForm.result"
            type="textarea"
            :rows="3"
            placeholder="请输入处理结果"
          />
        </el-form-item>
        <el-form-item label="处理人员" prop="worker">
          <el-input v-model="processForm.worker" placeholder="请输入处理人员姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="processDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProcess">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="addDialogVisible"
      title="添加违规记录"
      width="500px"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addRules"
        label-width="100px"
      >
        <el-form-item label="业主" prop="owner_id">
          <el-select
            v-model="addForm.owner_id"
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
            v-model="addForm.house_id"
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
        <el-form-item label="违规描述" prop="type">
          <el-input
            v-model="addForm.type"
            type="textarea"
            :rows="3"
            placeholder="请输入违规描述"
          />
        </el-form-item>
        <el-form-item label="违规金额" prop="fine_amount">
          <el-input-number
            v-model="addForm.fine_amount"
            :min="0"
            :precision="2"
            :step="100"
            placeholder="请输入违规金额"
          />
        </el-form-item>
        <el-form-item label="是否交费" prop="is_paid">
          <el-select v-model="addForm.is_paid" placeholder="请选择是否交费">
            <el-option label="已交费" :value="true" />
            <el-option label="未交费" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="收费人员" prop="worker">
          <el-input v-model="addForm.worker" placeholder="请输入收费人员姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAdd">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { violationAPI, ownerAPI, houseAPI } from '@/api'

const violationList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const processDialogVisible = ref(false)
const addDialogVisible = ref(false)
const processFormRef = ref(null)
const addFormRef = ref(null)
const ownerOptions = ref([])
const houseOptions = ref([])
const currentViolation = ref(null)

const searchForm = reactive({
  ownerNumber: '',
  houseNumber: ''
})

const processForm = reactive({
  result: '',
  worker: ''
})

const addForm = reactive({
  owner_id: '',
  house_id: '',
  type: '',
  fine_amount: 0,
  is_paid: false,
  worker: '',
  processed_at: new Date().toISOString().split('T')[0]
})

const processRules = {
  result: [
    { required: true, message: '请输入处理结果', trigger: 'blur' }
  ],
  worker: [
    { required: true, message: '请输入处理人员', trigger: 'blur' }
  ]
}

const addRules = {
  owner_id: [
    { required: true, message: '请选择业主', trigger: 'change' }
  ],
  house_id: [
    { required: true, message: '请选择房屋', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请输入违规描述', trigger: 'blur' }
  ],
  fine_amount: [
    { required: true, message: '请输入违规金额', trigger: 'blur' }
  ],
  is_paid: [
    { required: true, message: '请选择是否交费', trigger: 'change' }
  ],
  worker: [
    { required: true, message: '请输入收费人员', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      ownerNumber: searchForm.ownerNumber,
      houseNumber: searchForm.houseNumber
    }
    const res = await violationAPI.getList(params)
    if (res.code === 200) {
      violationList.value = res.data
      total.value = res.total
    } else {
      ElMessage.error(res.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取违规记录列表失败:', error)
    ElMessage.error(error.response?.data?.message || '获取数据失败，请重试')
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
  addForm.house_id = ''
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  searchForm.ownerNumber = ''
  searchForm.houseNumber = ''
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

const resetProcessForm = () => {
  processForm.result = ''
  processForm.worker = ''
}

const resetAddForm = () => {
  addForm.owner_id = ''
  addForm.house_id = ''
  addForm.type = ''
  addForm.fine_amount = 0
  addForm.is_paid = false
  addForm.worker = ''
  addForm.processed_at = new Date().toISOString().split('T')[0]
}

const handleAdd = () => {
  resetAddForm()
  addDialogVisible.value = true
}

const handleProcess = (row) => {
  currentViolation.value = row
  resetProcessForm()
  processDialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该违规记录吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await violationAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const submitProcess = async () => {
  if (!processFormRef.value) return
  await processFormRef.value.validate(async (valid) => {
    if (valid && currentViolation.value) {
      try {
        await violationAPI.process(currentViolation.value.id, {
          result: processForm.result,
          worker: processForm.worker,
          status: '已处理'
        })
        ElMessage.success('处理成功')
        processDialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error('处理失败')
      }
    }
  })
}

const submitAdd = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await violationAPI.add({
          owner_id: addForm.owner_id,
          house_id: addForm.house_id,
          type: addForm.type,
          fine_amount: addForm.fine_amount,
          status: addForm.is_paid ? '已处理' : '未处理',
          worker: addForm.worker,
          processed_at: addForm.processed_at
        })
        ElMessage.success('添加成功')
        addDialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error('添加失败')
      }
    }
  })
}

onMounted(() => {
  fetchData()
  fetchOwnerOptions()
  fetchHouseOptions()
})
</script>

<style scoped>
.violation-list {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 