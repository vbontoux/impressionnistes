<template>
  <div class="crew-members-view">
    <CrewMemberList />
  </div>
</template>

<script setup>
import CrewMemberList from '../components/CrewMemberList.vue';
</script>

<style scoped>
.crew-members-view {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
