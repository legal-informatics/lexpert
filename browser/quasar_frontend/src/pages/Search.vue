<template>
  <q-page class="flex items-start justify-center">
    <SearchForm v-on:results="results"></SearchForm>
    <ResultTable
      v-bind:items="items"
      v-bind:cols="visible_columns"
    ></ResultTable>
  </q-page>
</template>

<script>
import SearchForm from "components/SearchForm";
import ResultTable from "components/ResultTable";

export default {
  name: "PageSearch",

  components: {
    SearchForm,
    ResultTable
  },

  data() {
    return {
      items: null,
      visible_columns: ["o", "subtype", "area", "group", "actions"]
    };
  },

  methods: {
    results(results) {
      this.items = results;
    }
  }
};
</script>
