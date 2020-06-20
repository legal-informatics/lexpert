<template>
  <div class="q-pa-md">
    <q-table
      title="Rezultati pretrage"
      :data="results"
      :columns="columns"
      :visible-columns="visible_columns"
      v-if="results.length !== 0"
      row-key="name"
      flat
      bordered
      style="min-width: 1000px; max-width:1400px"
    >
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            dense
            round
            flat
            color="grey"
            @click="xhtml(props)"
            icon="img:statics/icons8-document-26.png"
          >
            <q-tooltip>XHTML</q-tooltip>
          </q-btn>
          <q-btn
            dense
            round
            flat
            color="grey"
            @click="xml(props)"
            icon="img:statics/icons8-xml-26.png"
          >
            <q-tooltip>XML</q-tooltip>
          </q-btn>
          <q-btn
            dense
            round
            flat
            color="grey"
            @click="pdf(props)"
            icon="img:statics/icons8-pdf-26.png"
          >
            <q-tooltip>PDF</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <q-dialog
      v-model="dialog"
      persistent
      :maximized="true"
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card class="bg-primary text-white">
        <q-bar>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip content-class="bg-white text-primary">Zatvori</q-tooltip>
          </q-btn>
        </q-bar>

        <!-- <q-card-section>
          <div class="text-h6">{{selected_row}}</div>
        </q-card-section> -->

        <q-card-section class="flex justify-center q-pt-none">
          <div class="document">
            <q-card-section class="flex justify-center">
              <div v-html="html" @click="handleClick"></div>
            </q-card-section>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { openURL } from "quasar";

export default {
  name: "ResultTable",
  props: ["items", "cols"],
  data() {
    return {
      results: [],
      columns: [
        {
          name: "o",
          required: true,
          label: "Naslov",
          align: "left",
          field: "o",
          style: "white-space: normal",
          sortable: true
        },
        {
          name: "subtype",
          align: "left",
          label: "Podtip",
          field: "subtype",
          style: "white-space: normal",
          sortable: true
        },
        {
          name: "area",
          align: "left",
          label: "Oblast",
          field: "area",
          style: "white-space: normal",
          sortable: true
        },
        {
          name: "group",
          align: "left",
          label: "Grupa",
          field: "group",
          style: "white-space: normal",
          sortable: true
        },
        {
          name: "s",
          align: "left",
          label: "URI",
          field: "s",
          sortable: false,
          style: "white-space: normal"
        },
        {
          name: "lng",
          align: "left",
          label: "Jezik",
          field: "lng",
          sortable: true,
          style: "white-space: normal"
        },
        {
          name: "date",
          align: "left",
          label: "Datum",
          field: "date",
          sortable: false,
          style: "white-space: normal"
        },
        { name: "actions", label: "Preuzimanje", field: "", align: "center" }
      ],
      visible_columns: this.cols,
      dialog: false,
      selected_row: null,
      html: null
    };
  },

  methods: {
    xhtml(props) {
      this.dialog = true;
      this.selected_row = props["row"]["o"];

      this.$axios
        .get(
          process.env.SERVERS[props["row"]["s"].split("#")[1].split("/")[5]] +
            props["row"]["s"].split("#")[1] +
            ".xhtml"
        )
        .then(response => {
          this.html = response.data;
        });
    },
    xml(props) {
      require("file-saver");

      this.$axios
        .get(
          process.env.SERVERS[props["row"]["s"].split("#")[1].split("/")[5]] +
            props["row"]["s"].split("#")[1] +
            ".xml",
          { responseType: "blob" }
        )
        .then(response => {
          var file = new Blob([response.data], {
            type: "application/xml"
          });

          // Generate file download directly in the browser !
          saveAs(file, props["row"]["s"].split("#")[1] + ".xml");
        });
    },
    pdf(props) {
      require("file-saver");

      this.$axios
        .get(
          process.env.SERVERS[props["row"]["s"].split("#")[1].split("/")[5]] +
            props["row"]["s"].split("#")[1] +
            ".pdf",
          { responseType: "blob" }
        )
        .then(response => {
          console.log(response);

          var file = new Blob([response.data], {
            type: "application/pdf"
          });

          // Generate file download directly in the browser !
          saveAs(file, props["row"]["s"].split("#")[1] + ".pdf");
        });
    },
    handleClick(e) {
      e.preventDefault();
      if (e.target.matches(".link")) {
        console.log(
          "klik na link: " +
            process.env.SERVERS[e.target.href.split("#")[1].split("/")[5]] +
            e.target.href.split("#")[1]
        );
        openURL(
          process.env.SERVERS[e.target.href.split("#")[1].split("/")[5]] +
            e.target.href.split("#")[1]
        );
      }
    }
  },
  watch: {
    items: function(newVal, oldVal) {
      // watch it
      this.results = this.items;
    }
  }
};
</script>

<style scoped lang="sass">
.document
  max-width: 900px
  background: white
  color: black
  padding-left: 5em
  padding-right: 5em
  padding-top: 3em
  padding-bottom: 3em
  margin-top: 5em
  margin-bottom: 5em

.my-sticky-header-table
  /* height or max-height is important */
  height: 310px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #c1f4cd

  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0

  /* this is when the loading indicator appears */
  &.q-table--loading thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
</style>
