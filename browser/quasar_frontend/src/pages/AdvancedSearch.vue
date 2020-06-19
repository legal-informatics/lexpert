<template>
  <q-page class="flex items-start justify-center">
    <AdvancedSearchForm v-on:results="results"></AdvancedSearchForm>
    <ResultTable
      v-bind:items="items"
      v-bind:cols="visible_columns"
    ></ResultTable>
  </q-page>
</template>

<script>
import AdvancedSearchForm from "components/AdvancedSearchForm";
import ResultTable from "components/ResultTable";

export default {
  name: "PageAdvancedSearch",

  components: {
    AdvancedSearchForm,
    ResultTable
  },

  data() {
    return {
      items: null,
      visible_columns: [
        "o",
        "subtype",
        "area",
        "group",
        "actions",
        "lng",
        "date"
      ]
    };
  },

  methods: {
    results(results) {
      this.items = results;
    }
  }
};
</script>
