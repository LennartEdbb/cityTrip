import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/HomeView.vue"
import LoginView from "@/views/LoginView.vue"
import SettingsView from "@/views/SettingsView.vue"
import RegisterView from "@/views/RegisterView.vue"

const routes = [
  {
    path: "/",
    name: "Map",
    component: MapView
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView
  },
  {
    path: "/register",
    name: "Register",
    component: RegisterView,
  },
  {
    path: "/settings",
    name: "Settings",
    component: SettingsView
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
