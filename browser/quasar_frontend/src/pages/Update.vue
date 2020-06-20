<template>
  <q-page class="flex items-start justify-center">
    <div class="q-pa-md">
      <div class="q-gutter-md">
        <div class="text-h4">Izmena dokumenta</div>
        <q-select
          v-if="options != null"
          v-model="selected"
          :options="options"
          label="Izaberite URI"
        />
        <q-uploader
          style="max-width: 300px"
          :factory="factoryFn"
          @added="added"
        />
      </div>
    </div>
  </q-page>
</template>

<script>
// import SearchForm from "components/SearchForm";
// import ResultTable from "components/ResultTable";

export default {
  name: "PageUpdate",

  components: {
    // SearchForm,
    // ResultTable
  },

  data() {
    return {
      // items: null
      model: null,
      selected: null,
      options: null
    };
  },

  methods: {
    factoryFn(files) {
      return {
        url: process.env.SERVERS[this.selected.split("/")[5]] + this.selected,
        method: "PUT",
        headers: [{ name: "Content-Type", value: "application/xml" }]
      };
    },
    added: function(files) {
      var parseString = require("xml2js").parseString;
      var reader = new FileReader();

      var help = this;

      reader.readAsText(files[0]);
      reader.onload = function(e) {
        var rawLog = reader.result;

        parseString(rawLog, function(err, result) {
          help.options = [
            result["akomaNtoso"]["act"][0]["meta"][0]["identification"]["0"][
              "FRBRManifestation"
            ]["0"]["FRBRuri"][0]["$"]["value"],
            result["akomaNtoso"]["act"][0]["meta"][0]["identification"]["0"][
              "FRBRExpression"
            ]["0"]["FRBRuri"][0]["$"]["value"],
            result["akomaNtoso"]["act"][0]["meta"][0]["identification"]["0"][
              "FRBRWork"
            ]["0"]["FRBRuri"][0]["$"]["value"]
          ];
          help.selected = help.options[0];
        });
      };
    }
  }
};
</script>
