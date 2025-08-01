<template>
  <base-list
    title="维修管理"
    :data="repairList"
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
      <el-form-item label="报修人">
        <el-select
          v-model="searchForm.ownerName"
          filterable
          remote
          :remote-method="searchOwners"
          placeholder="请输入业主姓名搜索"
          clearable
        >
          <el-option
            v-for="owner in ownerOptions"
            :key="owner.id"
            :label="owner.name"
            :value="owner.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="房屋编号">
        <el-select
          v-model="searchForm.houseNumber"
          filterable
          remote
          :remote-method="searchHouses"
          placeholder="请输入房屋编号搜索"
          clearable
        >
          <el-option
            v-for="house in houseOptions"
            :key="house.id"
            :label="house.number"
            :value="house.number"
          />
        </el-select>
      </el-form-item>
    </template>

    <!-- 表格列插槽 -->
    <el-table-column prop="id" label="维修编号" width="100" />
    <el-table-column prop="owner_name" label="报修人" width="120" />
    <el-table-column prop="house_number" label="房屋编号" width="120" />
    <el-table-column prop="content" label="维修内容" show-overflow-tooltip />
    <el-table-column prop="repair_date" label="报修时间" width="180" />
    <el-table-column prop="worker_name" label="维修工" width="100" />
    <el-table-column prop="finish_date" label="完成时间" width="180" />
    <el-table-column prop="cost" label="维修费用" width="100" />
    <el-table-column label="操作" width="120" fixed="right">
      <template #default="{ row }">
        <el-button 
          type="success" 
          size="small" 
          @click="handleComplete(row)"
          v-if="!row.finish_date"
        >
          完成维修
        </el-button>
      </template>
    </el-table-column>
  </base-list>

  <!-- 添加维修单对话框 -->
  <el-dialog
    v-model="addDialogVisible"
    title="添加维修单"
    width="500px"
  >
    <el-form
      ref="addFormRef"
      :model="addForm"
      :rules="addRules"
      label-width="100px"
    >
      <el-form-item label="报修人" prop="owner_id">
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
      <el-form-item label="维修工" prop="worker_id">
        <el-select
          v-model="addForm.worker_id"
          placeholder="请选择维修工"
        >
          <el-option
            v-for="worker in workerOptions"
            :key="worker.id"
            :label="worker.name"
            :value="worker.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="维修内容" prop="content">
        <el-input
          v-model="addForm.content"
          type="textarea"
          :rows="3"
          placeholder="请输入维修内容"
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

  <!-- 完成维修对话框 -->
  <el-dialog
    v-model="completeDialogVisible"
    title="完成维修"
    width="500px"
  >
    <el-form
      ref="completeFormRef"
      :model="completeForm"
      :rules="completeRules"
      label-width="100px"
    >
      <el-form-item label="维修费用" prop="cost">
        <el-input-number
          v-model="completeForm.cost"
          :min="0"
          :precision="2"
          :step="100"
          placeholder="请输入维修费用"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitComplete">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import BaseList from '../components/BaseList.vue'
import { repairAPI, ownerAPI, houseAPI, workerAPI } from '../api'

const repairList = ref([])
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
const workerOptions = ref([])

// 业主的房屋列表
const ownerHouses = ref([])

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

// 获取维修工列表
const fetchWorkers = async () => {
  try {
    const res = await workerAPI.getList()
    workerOptions.value = res.data
  } catch (error) {
    console.error('获取维修工列表失败:', error)
    ElMessage.error('获取维修工列表失败')
  }
}

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

// 添加维修单相关
const addDialogVisible = ref(false)
const addFormRef = ref(null)
const addForm = ref({
  owner_id: '',
  house_id: '',
  worker_id: '',
  content: ''
})
const addRules = {
  owner_id: [{ required: true, message: '请选择报修人', trigger: 'change' }],
  house_id: [{ required: true, message: '请选择房屋', trigger: 'change' }],
  worker_id: [{ required: true, message: '请选择维修工', trigger: 'change' }],
  content: [{ required: true, message: '请输入维修内容', trigger: 'blur' }]
}

// 完成维修相关
const completeDialogVisible = ref(false)
const completeFormRef = ref(null)
const completeForm = ref({
  cost: 0
})
const completeRules = {
  cost: [{ required: true, message: '请输入维修费用', trigger: 'blur' }]
}
const currentRepair = ref(null)

// 获取维修单列表数据
const fetchRepairList = async () => {
  loading.value = true
  try {
    const res = await repairAPI.getList({
      page: currentPage.value,
      size: pageSize.value,
      ownerName: searchForm.value.ownerName,
      houseNumber: searchForm.value.houseNumber
    })
    repairList.value = res.data
    total.value = res.total
  } catch (error) {
    console.error('获取维修单列表失败:', error)
    ElMessage.error('获取维修单列表失败')
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchRepairList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchRepairList()
}

// 处理添加维修单
const handleAdd = () => {
  addForm.value = {
    owner_id: '',
    house_id: '',
    worker_id: '',
    content: ''
  }
  ownerHouses.value = []
  addDialogVisible.value = true
  fetchWorkers() // 获取维修工列表
}

const submitAdd = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await repairAPI.add(addForm.value)
        ElMessage.success('添加成功')
        addDialogVisible.value = false
        fetchRepairList()
      } catch (error) {
        console.error('添加维修单失败:', error)
        ElMessage.error('添加维修单失败')
      }
    }
  })
}

// 处理完成维修
const handleComplete = (row) => {
  currentRepair.value = row
  completeForm.value = {
    cost: 0
  }
  completeDialogVisible.value = true
}

const submitComplete = async () => {
  if (!completeFormRef.value || !currentRepair.value) return
  
  await completeFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await repairAPI.complete(currentRepair.value.id, completeForm.value)
        ElMessage.success('完成成功')
        completeDialogVisible.value = false
        fetchRepairList()
      } catch (error) {
        console.error('完成维修失败:', error)
        ElMessage.error('完成维修失败')
      }
    }
  })
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchRepairList()
}

// 处理重置
const handleReset = () => {
  searchForm.value.ownerName = ''
  searchForm.value.houseNumber = ''
  currentPage.value = 1
  fetchRepairList()
}

onMounted(() => {
  fetchRepairList()
})
</script> 