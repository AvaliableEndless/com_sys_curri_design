<template>
  <el-container class="app-container">
    <el-aside width="200px" class="aside">
      <div class="logo">社区物业管理系统</div>
      <el-menu
        :router="true"
        :default-active="$route.path"
        class="menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/owners">
          <el-icon><User /></el-icon>
          <span>业主管理</span>
        </el-menu-item>
        <el-menu-item index="/houses">
          <el-icon><House /></el-icon>
          <span>房屋管理</span>
        </el-menu-item>
        <el-menu-item index="/payment-bills">
          <el-icon><Money /></el-icon>
          <span>缴费管理</span>
        </el-menu-item>
        <el-menu-item index="/violation-bills">
          <el-icon><Warning /></el-icon>
          <span>违规管理</span>
        </el-menu-item>
        <el-menu-item index="/complaint-bills">
          <el-icon><ChatDotRound /></el-icon>
          <span>投诉管理</span>
        </el-menu-item>
        <el-menu-item index="/repair-bills">
          <el-icon><Tools /></el-icon>
          <span>报修管理</span>
        </el-menu-item>
        <el-menu-item index="/repair-workers">
          <el-icon><UserFilled /></el-icon>
          <span>维修人员管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="toggle-icon" @click="toggleSidebar">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ username }}
              <el-icon><CaretBottom /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  User,
  House,
  Money,
  Warning,
  ChatDotRound,
  Tools,
  UserFilled,
  Fold,
  Expand,
  CaretBottom
} from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    User,
    House,
    Money,
    Warning,
    ChatDotRound,
    Tools,
    UserFilled,
    Fold,
    Expand,
    CaretBottom
  },
  setup() {
    const router = useRouter()
    const isCollapse = ref(false)
    const username = computed(() => {
      const storedUsername = localStorage.getItem('username')
      return storedUsername ? storedUsername : '未登录'
    })

    const toggleSidebar = () => {
      isCollapse.value = !isCollapse.value
    }

    const handleCommand = (command) => {
      if (command === 'logout') {
        // 清除登录状态
        localStorage.removeItem('isAuthenticated')
        localStorage.removeItem('username')
        // 跳转到登录页
        router.push('/login')
      }
    }

    return {
      isCollapse,
      username,
      toggleSidebar,
      handleCommand
    }
  }
}
</script>

<style>
.app-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  color: #fff;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  background-color: #2b3649;
}

.menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-icon {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info .el-icon {
  margin-left: 5px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style> 