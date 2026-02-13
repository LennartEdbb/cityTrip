import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/HomeView.vue"

const routes = [
  {
    path: "/",
    name: "Map",
    component: MapView
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
