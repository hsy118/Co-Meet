<template>
  <div class="reccom">
    <Navbar />
    <Address />
    <Graph/>
    <Explain />
  </div>
</template>

<script>
import Graph from "../components/Graph.vue"
import Address from "../components/Address.vue"
import Explain from "../components/Explain.vue"
import Navbar from "../components/navbar.vue"

export default {
  components: {
    Navbar,
    Address,
    Graph,
    Explain,
  },
}
</script>

<style>
  .reccom {
    width: 93vw;
    margin: 10% auto 0 auto;
  }
</style>