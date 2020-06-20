<template>
  <div class="q-pa-md" style="min-width: 600px">
    <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
      <q-input
        filled
        v-model="query"
        label="Pojam za pretragu"
        hint="Pojam za pretragu"
      />

      <q-toggle v-model="split" label="Sve ove reči" />

      <div class="flex justify-center">
        <q-btn label="Pretraži" type="submit" color="primary" />
        <q-btn
          label="Resetuj"
          type="reset"
          color="primary"
          flat
          class="q-ml-sm"
        />
      </div>
    </q-form>
  </div>
</template>

<script>
export default {
  name: "SearchForm",
  data() {
    return {
      query: null,
      split: false,
      result: null
    };
  },

  methods: {
    onSubmit() {
      this.result = null;
      this.$emit("results", this.result);

      for (var key in process.env.SERVERS) {
        console.log(process.env.SERVERS[key]);

        this.$axios
          .post(process.env.SERVERS[key] + "/simple_search", {
            query: this.query,
            split: this.split
          })
          .then(response => {
            this.result = response.data;
            this.$emit("results", this.result);

            if (this.result.length === 0) {
              this.$q.notify({
                message: "Pretraga nije dala rezultate",
                caption: "Pokušajte pretragu sa drugim pojmom."
              });
            }
          });
      }
      // this.$axios
      //   .post("http://127.0.0.1:5000/simple_search", {
      //     query: this.query,
      //     split: this.split
      //   })
      //   .then(response => {
      //     this.result = response.data;
      //     this.$emit("results", this.result);

      //     if (this.result.length === 0) {
      //       this.$q.notify({
      //         message: "Pretraga nije dala rezultate",
      //         caption: "Pokušajte pretragu sa drugim pojmom."
      //       });
      //     }
      //   });
    },

    onReset() {
      this.query = null;
      this.split = false;
      // console.log(process.env.SERVERS.a001);

      for (var key in process.env.SERVERS) {
        console.log(process.env.SERVERS[key]);
      }
    }
  }
};
</script>
