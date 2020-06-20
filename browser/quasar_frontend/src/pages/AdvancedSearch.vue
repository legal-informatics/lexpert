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
      if (results == null) {
        this.items = null;
      } else {
        if (this.items == null) this.items = results;
        else {
          console.log("res");
          console.log(results);
          console.log("loop");
          for (let i = 0; i < results.length; i++) {
            this.items.push(results[i]);
          }
        }

        console.log(this.items);
      }
    }
  }
};
</script>
