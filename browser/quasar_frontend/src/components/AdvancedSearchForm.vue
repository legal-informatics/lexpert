<template>
  <div class="q-pa-md" style="min-width: 600px">
    <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
      <div class="row justify-between">
        <q-select
          class="col-5"
          filled
          v-model="selected_subregister"
          :options="subregisters"
          label="Podregistar"
        />
        <q-select
          class="col-6"
          filled
          v-model="selected_subtype"
          :options="subtypes"
          label="Podtip"
        />
      </div>
      <q-select
        filled
        v-model="selected_area"
        :options="areas"
        label="Oblast"
      />
      <q-select
        filled
        v-model="selected_group"
        :options="groups"
        label="Grupa"
      />
      <q-input filled v-model="search" label="Pojam za pretragu" />
      <div class="row justify-between">
        <q-toggle v-model="split" label="Sve ove reči" class="col-3" />

        <div class="col-4" style="max-width: 300px">
          <q-input label="Od" filled v-model="date_from">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy
                  ref="qDateProxy"
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date
                    v-model="date_from"
                    @input="() => $refs.qDateProxy.hide()"
                  />
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </div>

        <div class="col-4" style="max-width: 300px">
          <q-input label="Do" filled v-model="date_to">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy
                  ref="qDateProxy"
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date
                    v-model="date_to"
                    @input="() => $refs.qDateProxy.hide()"
                  />
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </div>
      </div>
      <q-input filled v-model="keywords" label="Ključne reči" />

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
import { date } from "quasar";

export default {
  name: "AdvancedSearchForm",
  data() {
    return {
      search: null,
      keywords: null,
      split: false,
      result: null,
      selected_subregister: null,
      selected_area: null,
      selected_group: null,
      selected_subtype: null,
      date_from: null,
      date_to: null,
      subregisters: [
        {
          label: "REPUBLIČKI PROPISI",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01"
        },
        {
          label: "PROPISI IZ OBLASTI PROSVETE",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02"
        },
        {
          label: "MEĐUNARODNI UGOVORI",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03"
        }
      ],
      areas: [],
      groups: [],
      subtypes: [
        {
          label: "Ustav",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#ustav"
        },
        {
          label: "Zakon",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#zakon"
        },
        // {
        //   label: "Autentično/Obavezno tumačenje",
        //   value:
        //     "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01"
        // },
        {
          label: "Poslovnik",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#poslovnik"
        },
        {
          label: "Ukaz",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#ukaz"
        },
        {
          label: "Uredba",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#uredba"
        },
        {
          label: "Plan",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#plan"
        },
        {
          label: "Odluka",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#odluka"
        },
        {
          label: "Memorandum",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#memorandum"
        },
        {
          label: "Rezolucija",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#rezolucija"
        },
        {
          label: "Deklaracija",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#deklaracija"
        },
        {
          label: "Strategija",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#strategija"
        },
        {
          label: "Rešenje",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#rešenje"
        },
        {
          label: "Statut",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#statut"
        },
        {
          label: "Pravilnik",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#pravilnik"
        },
        {
          label: "Program",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#program"
        },
        {
          label: "Podatak",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#podatak"
        },
        {
          label: "Indeks",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#indeks"
        },
        {
          label: "Iznos, koeficijent",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#iznos_koeficijent"
        },
        {
          label: "Naredba",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#naredba"
        },
        {
          label: "Zaključak",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#zaključak"
        },
        {
          label: "Izveštaj",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#izveštaj"
        },
        {
          label: "Kodeks",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#kodeks"
        },
        {
          label: "Tarifa",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#tarifa"
        },
        {
          label: "Uputstvo, smernica, pravilo, preporuka",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#uputstvo_smernica_pravilo_preporuka"
        },
        {
          label: "Kriterijum, merilo",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#kriterijum_merilo"
        },
        {
          label: "Spisak, lista",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#spisak_lista"
        },
        {
          label: "Objašnjenje, mišljenje",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#objašnjenje_mišljenje"
        },
        {
          label: "Rokovnik",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#rokovnik"
        },
        {
          label: "Ugovor",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#ugovor"
        },
        {
          label: "Kolektivni ugovor",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#kolektivni_ugovor"
        },
        {
          label: "Ispravka",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#ispravka"
        },
        {
          label: "Sporazum",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#sporazum"
        },
        {
          label: "Konvencija",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#konvencija"
        },
        {
          label: "Protokol",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#protokol"
        },
        {
          label: "Ostalo",
          value:
            "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#ostalo"
        }
      ]
    };
  },

  methods: {
    onSubmit() {
      // console.log(this.selected_subregister.value);
      // console.log(this.selected_area.value);
      // console.log(this.selected_group.value);
      // console.log(this.selected_subtype.value);
      // console.log(this.search);
      // console.log(this.split);

      const data = {
        ...(this.selected_subregister != null && {
          subregister: this.selected_subregister.value
        }),
        ...(this.selected_area != null && {
          area: this.selected_area.value
        }),
        ...(this.selected_group != null && {
          group: this.selected_group.value
        }),
        ...(this.selected_subtype != null && {
          subtype: this.selected_subtype.value
        }),
        ...(this.search != null &&
          this.search != "" && {
            search: this.search
          }),
        ...(this.split != null &&
          this.search != null &&
          this.search != "" && {
            split: this.split
          }),
        ...(this.keywords != null &&
          this.keywords != "" && {
            keywords: this.keywords
          }),
        ...(this.date_from != null && {
          date_from: date.formatDate(this.date_from, "YYYY-MM-DD")
        }),
        ...(this.date_to != null &&
          this.date_to != "" && {
            date_to: date.formatDate(this.date_to, "YYYY-MM-DD")
          })
      };

      // console.log(data);
      // // check if object is empty
      // console.log(
      //   Object.keys(data).length === 0 && data.constructor === Object
      // );

      this.$axios.post("http://127.0.0.1:5000/search", data).then(response => {
        var help = response.data;

        for (let i = 0; i < help.length; i++) {
          help[i].s = help[i].exp;

          help[i].date = date.formatDate(help[i].date, "DD. MMMM YYYY.", {
            months: [
              "Januar",
              "Februar",
              "Mart",
              "April",
              "Maj",
              "Jun",
              "Jul",
              "Avgust",
              "Septembar",
              "Oktobar",
              "Novembar",
              "Decembar"
            ]
          });

          delete help[i].exp;
        }

        this.result = help;
        this.$emit("results", this.result);

        if (this.result.length === 0) {
          this.$q.notify({
            message: "Pretraga nije dala rezultate",
            caption: "Pokušajte pretragu sa drugim pojmom."
          });
        }
      });
    },

    onReset() {
      this.search = null;
      this.split = false;
      this.selected_subregister = null;
      this.selected_area = null;
      this.selected_group = null;
      this.selected_subtype = null;
      this.keywords = null;
      this.date_from = null;
      this.date_to = null;
    }
  },
  watch: {
    selected_subregister: function(newVal, oldVal) {
      // watch it
      this.selected_area = null;
      switch (newVal.label) {
        case "REPUBLIČKI PROPISI":
          this.areas = [
            {
              label: "I	DRŽAVNO UREĐENJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01"
            },
            {
              label: "II	ODBRANA, VOJSKA I UNUTRAŠNJI POSLOVI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02"
            },
            {
              label: "III	PRAVOSUĐE, KAZNENO ZAKONODAVSTVO I POSTUPCI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03"
            },
            {
              label: "IV	JAVNI PRIHODI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04"
            },
            {
              label:
                "V	MONETARNI SISTEM, FINANSIJSKE ORGANIZACIJE I FINANSIJSKO POSLOVANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05"
            },
            {
              label: "VI	SVOJINSKI I OBLIGACIONI, PORODIČNI I BRAČNI ODNOSI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06"
            },
            {
              label: "VII	RADNI ODNOSI I ZAPOŠLJAVANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07"
            },
            {
              label: "VIII	RAZVOJ",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08"
            },
            {
              label:
                "IX	OPŠTI PRIVREDNI PROPISI I EKONOMSKI ODNOSI SA INOSTRANSTVOM",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09"
            },
            {
              label: "X	DOBRA OD OPŠTEG INTERESA I ŽIVOTNA SREDINA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10"
            },
            {
              label: "XI	TRGOVINA, TURIZAM I UGOSTITELJSTVO",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g11"
            },
            {
              label:
                "XII	GRAĐEVINARSTVO, GRAĐEVINSKO ZEMLJIŠTE I KOMUNALNOSTAMBENE DELATNOSTI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12"
            },
            {
              label: "XIII	POLJOPRIVREDNA DELATNOST",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13"
            },
            {
              label: "XIV	SAOBRAĆAJ, VEZE I ENERGETIKA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14"
            },
            {
              label:
                "XV	JAVNE USTANOVE, NAUKA, PROSVETA, KULTURA, INFORMISANJE I SPORT",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15"
            },
            {
              label:
                "XVI	SOCIJALNO OSIGURANJE, ZDRAVSTVENA, SOCIJALNA I BORAČKA ZAŠTITA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16"
            }
          ];
          break;
        case "PROPISI IZ OBLASTI PROSVETE":
          this.areas = [
            {
              label: "I	OSNOVI OBRAZOVANJA I VASPITANJA, UDŽBENICI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g01"
            },
            {
              label: "II	PREDŠKOLSKO I OSNOVNO OBRAZOVANJE I VASPITANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g02"
            },
            {
              label: "III	GIMNAZIJE, STRUČNE ŠKOLE I OBRAZOVANJE ODRASLIH",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g03"
            }
          ];
          break;
        case "MEĐUNARODNI UGOVORI":
          this.areas = [
            {
              label:
                "I	OSNOVNA PRAVA I SLOBODE, NJIHOVA ZAŠTITA I SPOLJNA POLITIKA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g01"
            },
            {
              label: "II	BEZBEDNOSNA I ODBRAMBENA POLITIKA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02"
            },
            {
              label:
                "III	PRAVOSUĐE, KAZNENO ZAKONODAVSTVO I MEĐUNARODNA PRAVNA POMOĆ",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03"
            },
            {
              label: "IV	JAVNI PRIHODI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g04"
            },
            {
              label:
                "V	MONETARNA POLITIKA, FINANSIJSKE ORGANIZACIJE I FINANSIJSKO POSLOVANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g05"
            },
            {
              label:
                "VI	IMOVINSKI, BRAČNI I PORODIČNI ODNOSI, PRAVO INTELEKTUALNE SVOJINE I NASLEĐIVANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06"
            },
            {
              label: "VII	RAD I ZAPOŠLJAVANJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g07"
            },
            {
              label: "VIII	RAZVOJ I INFORMACIONE TEHNOLOGIJE",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g08"
            },
            {
              label:
                "IX	PRAVO PRIVREDNIH DRUŠTAVA I EKONOMSKI ODNOSI SA INOSTRANSTVOM",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g09"
            },
            {
              label: "X	DOBRA OD OPŠTEG INTERESA I ŽIVOTNA SREDINA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10"
            },
            {
              label: "XI	TRGOVINA, TURIZAM I UGOSTITELJSTVO",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g11"
            },
            {
              label: "XII	GRAĐEVINARSTVO",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g12"
            },
            {
              label: "XIII	POLJOPRIVREDA I RURALNI RAZVOJ",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g13"
            },
            {
              label: "XIV	SAOBRAĆAJ, ELEKTRONSKE KOMUNIKACIJE I ENERGETIKA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14"
            },
            {
              label: "XV	OBRAZOVANJE, KULTURA, NAUKA, INFORMISANJE I SPORT",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g15"
            },
            {
              label: "XVI	SOCIJALNA POLITIKA I ZAŠTITA ZDRAVLJA",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16"
            },
            {
              label: "XVII	OSTALI MEĐUNARODNI UGOVORI",
              value:
                "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g17"
            }
          ];
          break;
      }
    },
    selected_area: function(newVal, oldVal) {
      // watch it
      this.selected_group = null;
      switch (this.selected_subregister.label) {
        case "REPUBLIČKI PROPISI":
          switch (newVal.label) {
            case "I	DRŽAVNO UREĐENJE":
              this.groups = [
                {
                  label: "1. Ustav",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a01"
                },
                {
                  label: "2. Grb, zastava, himna i pečat",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a02"
                },
                {
                  label: "3. Državljanstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a03"
                },
                {
                  label:
                    "4. Državni i drugi praznici, godišnjice i dani koji se posebno obeležavaju",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a04"
                },
                {
                  label: "5. Službena upotreba jezika i pisama",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a05"
                },
                {
                  label: "6. Narodna skupština",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a06"
                },
                {
                  label: "7. Predsednik Republike",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a07"
                },
                {
                  label: "8. Vlada i radna tela Vlade",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a08"
                },
                {
                  label: "9. Ustavni sud",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a09"
                },
                {
                  label: "10. Zaštitnik građana",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a10"
                },
                {
                  label:
                    "11. Državna uprava, upravna inspekcija i inspekcijski nadzor",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a11"
                },
                {
                  label: "12. Spoljni poslovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a12"
                },
                {
                  label: "13. Izbori, referendum i narodna inicijativa",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a13"
                },
                {
                  label:
                    "14. Udruženja, političke stranke, crkve, verske zajednice i druge organizacije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a14"
                },
                {
                  label:
                    "15. Zaštita ljudskih prava i prava pripadnika nacionalnih manjina",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a15"
                },
                {
                  label:
                    "16. Borba protiv korupcije, zaštita uzbunjivača i lobiranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a16"
                },
                {
                  label: "17. Teritorijalna organizacija i lokalna samouprava",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a17"
                },
                {
                  label: "18. Objavljivanje propisa",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a18"
                },
                {
                  label: "19. Matične knjige",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a19"
                },
                {
                  label: "20. Državna odlikovanja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a20"
                },
                {
                  label: "21. Dijaspora i Srbi u regionu",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g01_a21"
                }
              ];
              break;
            case "II	ODBRANA, VOJSKA I UNUTRAŠNJI POSLOVI":
              this.groups = [
                {
                  label: "1. Odbrana i bezbednost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a01"
                },
                {
                  label: "2. Vojska Srbije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a02"
                },
                {
                  label: "3. Vojna oprema, naoružanje i roba dvostruke namene",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a03"
                },
                {
                  label: "4. Policija, javni red i mir i javno okupljanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a04"
                },
                {
                  label: "5. Oružje, municija, opasne i eksplozivne materije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a05"
                },
                {
                  label: "6. Prebivalište i boravište",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a06"
                },
                {
                  label: "7. Državna granica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a07"
                },
                {
                  label: "8. Putne isprave",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a08"
                },
                {
                  label: "9. Boravak stranaca",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a09"
                },
                {
                  label: "10. Lično ime, lična karta, matični broj građana",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a10"
                },
                {
                  label: "11. Migracije, izbeglice i raseljena lica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a11"
                },
                {
                  label:
                    "12. Vanredne situacije (civilna zaštita, elementarne i druge nepogode)",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a12"
                },
                {
                  label: "13. Zaštita od požara",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a13"
                },
                {
                  label: "14. Detektivska delatnost i privatno obezbeđenje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g02_a14"
                }
              ];
              break;
            case "III	PRAVOSUĐE, KAZNENO ZAKONODAVSTVO I POSTUPCI":
              this.groups = [
                {
                  label: "1. Sud",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a01"
                },
                {
                  label: "2. Tužilaštvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a02"
                },
                {
                  label: "3. Pravobranilaštvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a03"
                },
                {
                  label:
                    "4. Advokatura, javno beležništvo i besplatna pravna pomoć",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a04"
                },
                {
                  label: "5. Veštačenje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a05"
                },
                {
                  label: "6. Pravosudna akademija i pravosudni ispit",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a06"
                },
                {
                  label: "7. Krivična dela i krivični postupak",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a07"
                },
                {
                  label: "8. Privredni prestupi i prekršaji",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a08"
                },
                {
                  label:
                    "9. Izvršenje krivičnih sankcija i alternativnih sankcija i mera",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a09"
                },
                {
                  label: "10. Rehabilitacija, amnestija i pomilovanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a10"
                },
                {
                  label:
                    "11. Postupci u oblasti građanskog prava, upravni i ostali postupci",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a11"
                },
                {
                  label:
                    "12. Overavanje potpisa, rukopisa, prepisa i overavanje isprava u međunarodnom prometu",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g03_a12"
                }
              ];
              break;
            case "IV	JAVNI PRIHODI":
              this.groups = [
                {
                  label: "1. Carine i druge uvozne dažbine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a01"
                },
                {
                  label: "2. Porezi i akcize",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a02"
                },
                {
                  label: "3. Takse i druge dažbine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a03"
                },
                {
                  label: "4. Javni zajmovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a04"
                },
                {
                  label: "5. Emisija državnih zapisa i hartija od vrednosti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a05"
                },
                {
                  label:
                    "6. Finansiranje nadležnosti države i teritorijalnih jedinica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a06"
                },
                {
                  label: "7. Igre na sreću",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a07"
                },
                {
                  label: "8. Propisi Evropske unije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a08"
                },
                {
                  label: "9. Propisi Svetske carinske organizacije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g04_a09"
                }
              ];
              break;
            case "V	MONETARNI SISTEM, FINANSIJSKE ORGANIZACIJE I FINANSIJSKO POSLOVANJE":
              this.groups = [
                {
                  label: "1. Narodna banka",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a01"
                },
                {
                  label: "2. Banke i druge finansijske organizacije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a02"
                },
                {
                  label: "3. Platni sistem i platne usluge",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a03"
                },
                {
                  label: "4. Računovodstvo i revizija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a04"
                },
                {
                  label:
                    "5. Sprečavanje pranja novca i finansiranja terorizma i ograničavanje raspolaganja imovinom",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a05"
                },
                {
                  label:
                    "6. Izdavanje, osnovna obeležja i puštanje u opticaj novčanica, kovanog novca i prigodnog kovanog novca",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a06"
                },
                {
                  label: "7. Hartije od vrednosti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a07"
                },
                {
                  label: "8. Kamate",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a08"
                },
                {
                  label: "9. Zaduživanje i garancije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g05_a09"
                }
              ];
              break;
            case "VI	SVOJINSKI I OBLIGACIONI, PORODIČNI I BRAČNI ODNOSI":
              this.groups = [
                {
                  label: "1. Oblici svojine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a01"
                },
                {
                  label: "2. Privatizacija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a02"
                },
                {
                  label:
                    "3. Eksproprijacija i drugi oblici ograničavanja svojine i vraćanje imovine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a03"
                },
                {
                  label:
                    "4. Založno pravo na pokretnim stvarima i nepokretnostima",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a04"
                },
                {
                  label: "5. Povraćaj i dodeljivanje zemljišta",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a05"
                },
                {
                  label: "6. Autorsko i srodna prava",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a06"
                },
                {
                  label: "7. Industrijska svojina i tehnička unapređenja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a07"
                },
                {
                  label: "8. Zadužbine, fondacije i fondovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a08"
                },
                {
                  label: "9. Premer i katastar",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a09"
                },
                {
                  label: "10. Nasleđivanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a10"
                },
                {
                  label:
                    "11. Opšti obligacioni odnosi, finansijski lizing i faktoring",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a11"
                },
                {
                  label: "12. Obligacioni odnosi u saobraćaju",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a12"
                },
                {
                  label: "13. Promet nepokretnosti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a13"
                },
                {
                  label: "14. Javno-privatno partnerstvo i koncesije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a14"
                },
                {
                  label: "15. Brak, porodica i sprečavanje nasilja u porodici",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g06_a15"
                }
              ];
              break;
            case "VII	RADNI ODNOSI I ZAPOŠLJAVANJE":
              this.groups = [
                {
                  label:
                    "1. Radni odnosi, zaštita na radu i evidencije u oblasti rada",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a01"
                },
                {
                  label:
                    "2. Radni odnosi u državnim organima, autonomnim pokrajinama i jedinicama lokalne samouprave",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a02"
                },
                {
                  label:
                    "3. Zapošljavanje i upućivanje zaposlenih na privremeni rad u inostranstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a03"
                },
                {
                  label: "4. Zarade, plate, naknade i druga primanja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a04"
                },
                {
                  label: "5. Štrajk",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a05"
                },
                {
                  label: "6. Kolektivni ugovori",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a06"
                },
                {
                  label: "7. Volontiranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a07"
                },
                {
                  label: "8. Psihološka delatnost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g07_a08"
                }
              ];
              break;
            case "VIII	RAZVOJ":
              this.groups = [
                {
                  label:
                    "1. Planiranje razvoja, regionalni razvoj i nerazvijena područja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a01"
                },
                {
                  label: "2. Statistika",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a02"
                },
                {
                  label: "3. Informacione tehnologije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a03"
                },
                {
                  label:
                    "4. Kvalitet predmeta opšte upotrebe i životnih namirnica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a04"
                },
                {
                  label: "5. Standardizacija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a05"
                },
                {
                  label: "6. Računanje vremena",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g08_a06"
                }
              ];
              break;
            case "IX	OPŠTI PRIVREDNI PROPISI I EKONOMSKI ODNOSI SA INOSTRANSTVOM":
              this.groups = [
                {
                  label: "1. Privredna društva, preduzeća i preduzetnici",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a01"
                },
                {
                  label: "2. Osnivački akti privrednih društava i preduzeća",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a02"
                },
                {
                  label: "3. Osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a03"
                },
                {
                  label: "4. Zadruge",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a04"
                },
                {
                  label: "5. Privredne komore",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a05"
                },
                {
                  label: "6. Slobodne zone",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a06"
                },
                {
                  label: "7. Spoljnotrgovinsko poslovanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a07"
                },
                {
                  label: "8. Devizno poslovanje i strana ulaganja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a08"
                },
                {
                  label: "9. Klasifikacija delatnosti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a09"
                },
                {
                  label: "10. Stečaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a10"
                },
                {
                  label: "11. Registracija privrednih subjekata",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a11"
                },
                {
                  label: "12. Otklanjanje posledica sankcija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g09_a12"
                }
              ];
              break;
            case "X	DOBRA OD OPŠTEG INTERESA I ŽIVOTNA SREDINA":
              this.groups = [
                {
                  label: "1. Zemljište",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a01"
                },
                {
                  label: "2. Vode",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a02"
                },
                {
                  label: "3. Vazduh",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a03"
                },
                {
                  label: "4. Rude i geološka istraživanja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a04"
                },
                {
                  label: "5. Šume i šumsko zemljište",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a05"
                },
                {
                  label: "6. Putevi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a06"
                },
                {
                  label: "7. Skijališta i žičare",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a07"
                },
                {
                  label: "8. Banje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a08"
                },
                {
                  label: "9. Divljač",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a09"
                },
                {
                  label: "10. Ribarstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a10"
                },
                {
                  label: "11. Životna sredina",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a11"
                },
                {
                  label: "12. Zaštita prirode",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a12"
                },
                {
                  label: "13. Nacionalni parkovi i zaštićena područja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a13"
                },
                {
                  label: "14. Zaštita od zračenja i nuklearna sigurnost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a14"
                },
                {
                  label: "15. Upravljanje otpadom",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a15"
                },
                {
                  label: "16. Hidrometeorološki poslovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g10_a16"
                }
              ];
              break;
            case "XI	TRGOVINA, TURIZAM I UGOSTITELJSTVO":
              this.groups = [
                {
                  label: "1. Trgovina, javne nabavke i zaštita potrošača",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g11_a01"
                },
                {
                  label: "2. Turizam i ugostiteljstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g11_a02"
                },
                {
                  label: "3. Zaštita konkurencije i kontrola državne pomoći",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g11_a03"
                },
                {
                  label: "4. Robne rezerve",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g11_a04"
                }
              ];
              break;
            case "XII	GRAĐEVINARSTVO, GRAĐEVINSKO ZEMLJIŠTE I KOMUNALNOSTAMBENE DELATNOSTI":
              this.groups = [
                {
                  label: "1. Planiranje i izgradnja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12_a01"
                },
                {
                  label: "2. Prostorni planovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12_a02"
                },
                {
                  label: "3. Stanovanje i održavanje stambenih zgrada",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12_a03"
                },
                {
                  label: "4. Komunalne delatnosti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12_a04"
                },
                {
                  label: "5. Groblja i sahranjivanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g12_a05"
                }
              ];
              break;
            case "XIII	POLJOPRIVREDNA DELATNOST":
              this.groups = [
                {
                  label: "1. Stočarstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a01"
                },
                {
                  label: "2. Zdravstvena zaštita životinja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a02"
                },
                {
                  label: "3. Seme i sadni materijal",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a03"
                },
                {
                  label: "4. Zaštita bilja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a04"
                },
                {
                  label: "5. Alkoholna pića",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a05"
                },
                {
                  label: "6. Duvan",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a06"
                },
                {
                  label: "7. Poljoprivreda i razvoj poljoprivrede",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g13_a07"
                }
              ];
              break;
            case "XIV	SAOBRAĆAJ, VEZE I ENERGETIKA":
              this.groups = [
                {
                  label: "1. Drumski saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a01"
                },
                {
                  label: "2. Vazdušni saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a02"
                },
                {
                  label: "3. Železnički saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a03"
                },
                {
                  label: "4. Vodni saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a04"
                },
                {
                  label:
                    "5. Istraživanje nesreća u saobraćaju, Transportna zajednica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a05"
                },
                {
                  label: "6. Elektronske komunikacije i PTT saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a06"
                },
                {
                  label: "7. Energetika",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a07"
                },
                {
                  label: "8. Auto-moto savez",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g14_a08"
                }
              ];
              break;
            case "XV	JAVNE USTANOVE, NAUKA, PROSVETA, KULTURA, INFORMISANJE I SPORT":
              this.groups = [
                {
                  label: "1. Osnovi obrazovanja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a01"
                },
                {
                  label: "2. Javne službe i javne ustanove",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a02"
                },
                {
                  label:
                    "3. Akademija nauka i umetnosti i srpska enciklopedija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a03"
                },
                {
                  label: "4. Naučnoistraživačka delatnost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a04"
                },
                {
                  label: "5. Visoko obrazovanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a05"
                },
                {
                  label: "6. Srednje obrazovanje i vaspitanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a06"
                },
                {
                  label: "7. Osnovno i predškolsko obrazovanje i vaspitanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a07"
                },
                {
                  label: "8. Učenički i studentski standard",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a08"
                },
                {
                  label: "9. Informisanje i oglašavanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a09"
                },
                {
                  label: "10. Kultura",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a10"
                },
                {
                  label: "11. Kulturna dobra",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a11"
                },
                {
                  label: "12. Izdavaštvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a12"
                },
                {
                  label: "13. Biblioteke, muzeji i arhivi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a13"
                },
                {
                  label: "14. Kinematografija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a14"
                },
                {
                  label: "15. Sport",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g15_a15"
                }
              ];
              break;
            case "XVI	SOCIJALNO OSIGURANJE, ZDRAVSTVENA, SOCIJALNA I BORAČKA ZAŠTITA":
              this.groups = [
                {
                  label: "1. Penzijsko i invalidsko osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a01"
                },
                {
                  label: "2. Zdravstvena zaštita",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a02"
                },
                {
                  label: "3. Osnivački akti zdravstvenih ustanova",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a03"
                },
                {
                  label: "4. Zdravstveno osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a04"
                },
                {
                  label:
                    "5. Zdravstvena dokumentacija i evidencije u oblasti zdravstva",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a05"
                },
                {
                  label: "6. Transplantacije i transfuziološka delatnost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a06"
                },
                {
                  label: "7. Zaštita genetičkog i reproduktivnog zdravlja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a07"
                },
                {
                  label: "8. Komore zdravstvenih radnika",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a08"
                },
                {
                  label: "9. Doprinosi za obavezno socijalno osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a09"
                },
                {
                  label: "10. Socijalna zaštita i društvena briga o deci",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a10"
                },
                {
                  label: "11. Boračka zaštita",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a11"
                },
                {
                  label: "12. Zaštita osoba sa invaliditetom",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a12"
                },
                {
                  label:
                    "13. Humanitarne organizacije, donacije i humanitarna pomoć",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a13"
                },
                {
                  label:
                    "14. Proizvodnja i promet lekova, otrovnih materija i opojnih droga",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s01_g16_a14"
                }
              ];
              break;
          }
          break;
        case "PROPISI IZ OBLASTI PROSVETE":
          switch (newVal.label) {
            case "I	OSNOVI OBRAZOVANJA I VASPITANJA, UDŽBENICI":
              this.groups = [
                {
                  label: "1. Obrazovanje i vaspitanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g01_a01"
                },
                {
                  label: "2. Udžbenici",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g01_a02"
                }
              ];
              break;
            case "II	PREDŠKOLSKO I OSNOVNO OBRAZOVANJE I VASPITANJE":
              this.groups = [
                {
                  label: "1. Predškolsko vaspitanje i obrazovanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g02_a01"
                },
                {
                  label: "2. Osnovno obrazovanje i vaspitanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g02_a02"
                }
              ];
              break;
            case "III	GIMNAZIJE, STRUČNE ŠKOLE I OBRAZOVANJE ODRASLIH":
              this.groups = [
                {
                  label: "1. Gimnazije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g03_a01"
                },
                {
                  label: "2. Stručne škole",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g03_a02"
                },
                {
                  label: "3. Zajednički predmeti za srednje škole",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g03_a03"
                },
                {
                  label: "4. Obrazovanje odraslih",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s02_g03_a04"
                }
              ];
              break;
          }
          break;
        case "MEĐUNARODNI UGOVORI":
          switch (newVal.label) {
            case "I	OSNOVNA PRAVA I SLOBODE, NJIHOVA ZAŠTITA I SPOLJNA POLITIKA":
              this.groups = [
                {
                  label:
                    "1. Zaštita ljudskih prava i prava pripadnika nacionalnih manjina",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g01_a01"
                },
                {
                  label: "2. Spoljna politika",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g01_a02"
                },
                {
                  label:
                    "3. Zaključivanje, važenje i sukcesija međunarodnih ugovora",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g01_a03"
                },
                {
                  label: "4. Razmena zvaničnih publikacija",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g01_a04"
                }
              ];
              break;
            case "II	BEZBEDNOSNA I ODBRAMBENA POLITIKA":
              this.groups = [
                {
                  label: "1. Odbrana i bezbednost",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a01"
                },
                {
                  label: "2. Vojska",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a02"
                },
                {
                  label:
                    "3. Vojna oprema, naoružanje, opasne i eksplozivne materije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a03"
                },
                {
                  label: "4. Policijska saradnja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a04"
                },
                {
                  label: "5. Prelazak državne granice",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a05"
                },
                {
                  label: "6. Državljanstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a06"
                },
                {
                  label: "7. Putne isprave",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a07"
                },
                {
                  label: "8. Migraciona politika, izbeglice i raseljena lica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a08"
                },
                {
                  label: "9. Matične knjige",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a09"
                },
                {
                  label:
                    "10. Vanredne situacije, civilna zaštita, elementarne i druge nepogode",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g02_a10"
                }
              ];
              break;
            case "III	PRAVOSUĐE, KAZNENO ZAKONODAVSTVO I MEĐUNARODNA PRAVNA POMOĆ":
              this.groups = [
                {
                  label: "1. Saradnja u oblasti pravosuđa",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a01"
                },
                {
                  label: "2. Sud",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a02"
                },
                {
                  label: "3. Međunarodna pravna pomoć",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a03"
                },
                {
                  label: "4. Krivična dela",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a04"
                },
                {
                  label: "5. Izvršenje kazni",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a05"
                },
                {
                  label: "6. Postupci",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g03_a06"
                }
              ];
              break;
            case "IV	JAVNI PRIHODI":
              this.groups = [
                {
                  label: "1. Carine i druge uvozne dažbine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g04_a01"
                },
                {
                  label: "2. Oporezivanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g04_a02"
                },
                {
                  label: "3. Takse",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g04_a03"
                }
              ];
              break;
            case "V	MONETARNA POLITIKA, FINANSIJSKE ORGANIZACIJE I FINANSIJSKO POSLOVANJE":
              this.groups = [
                {
                  label: "1. Banke i druge finansijske organizacije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g05_a01"
                },
                {
                  label: "2. Platni promet",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g05_a02"
                },
                {
                  label:
                    "3. Zaduživanje u inostranstvu, donacije i bespovratna pomoć",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g05_a03"
                }
              ];
              break;
            case "VI	IMOVINSKI, BRAČNI I PORODIČNI ODNOSI, PRAVO INTELEKTUALNE SVOJINE I NASLEĐIVANJE":
              this.groups = [
                {
                  label: "1. Imovinski odnosi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06_a01"
                },
                {
                  label:
                    "2. Eksproprijacija i drugi oblici ograničavanja svojine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06_a02"
                },
                {
                  label: "3. Prava intelektualne svojine",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06_a03"
                },
                {
                  label: "4. Nasleđivanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06_a04"
                },
                {
                  label: "5. Brak i porodica",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g06_a05"
                }
              ];
              break;
            case "VII	RAD I ZAPOŠLJAVANJE":
              this.groups = [
                {
                  label: "1. Rad, zapošljavanje i zaštita na radu",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g07_a01"
                },
                {
                  label: "2. Akti Međunarodne organizacije rada (MOR)",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g07_a02"
                }
              ];
              break;
            case "VIII	RAZVOJ I INFORMACIONE TEHNOLOGIJE":
              this.groups = [
                {
                  label:
                    "1. Planiranje razvoja, regionalni razvoj i nerazvijena područja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g08_a01"
                },
                {
                  label: "2. Informacione tehnologije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g08_a02"
                }
              ];
              break;
            case "IX	PRAVO PRIVREDNIH DRUŠTAVA I EKONOMSKI ODNOSI SA INOSTRANSTVOM":
              this.groups = [
                {
                  label: "1. Privredna društva",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g09_a01"
                },
                {
                  label: "2. Kreditni poslovi sa inostranstvom",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g09_a02"
                },
                {
                  label: "3. Strana ulaganja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g09_a03"
                },
                {
                  label: "4. Međunarodna privredna i tehnička saradnja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g09_a04"
                }
              ];
              break;
            case "X	DOBRA OD OPŠTEG INTERESA I ŽIVOTNA SREDINA":
              this.groups = [
                {
                  label: "1. Vode",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10_a01"
                },
                {
                  label: "2. Ribarstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10_a02"
                },
                {
                  label: "3. Životna sredina",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10_a03"
                },
                {
                  label: "4. Rude i geološka istraživanja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10_a04"
                },
                {
                  label: "5. Hidrometeorološki poslovi",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g10_a05"
                }
              ];
              break;
            case "XI	TRGOVINA, TURIZAM I UGOSTITELJSTVO":
              this.groups = [
                {
                  label: "1. Trgovina",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g11_a01"
                },
                {
                  label: "2. Turizam i ugostiteljstvo",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g11_a02"
                }
              ];
              break;
            case "XII	GRAĐEVINARSTVO":
              this.groups = [
                {
                  label: "1. Izgradnja objekata",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g12_a01"
                }
              ];
              break;
            case "XIII	POLJOPRIVREDA I RURALNI RAZVOJ":
              this.groups = [
                {
                  label: "1. Veterinarstvo i zdravstvena zaštita životinja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g13_a01"
                },
                {
                  label: "2. Seme, sadni materijal i zaštita bilja",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g13_a02"
                },
                {
                  label: "3. Poljoprivredna služba i razvoj poljoprivrede",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g13_a03"
                }
              ];
              break;
            case "XIV	SAOBRAĆAJ, ELEKTRONSKE KOMUNIKACIJE I ENERGETIKA":
              this.groups = [
                {
                  label: "1. Drumski saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a01"
                },
                {
                  label: "2. Vazdušni saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a02"
                },
                {
                  label: "3. Železnički saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a03"
                },
                {
                  label: "4. Pomorska i unutrašnja plovidba",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a04"
                },
                {
                  label: "5. Elektronske komunikacije i poštanski saobraćaj",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a05"
                },
                {
                  label: "6. Ugovori u saobraćaju",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a06"
                },
                {
                  label: "7. Energetika",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g14_a07"
                }
              ];
              break;
            case "XV	OBRAZOVANJE, KULTURA, NAUKA, INFORMISANJE I SPORT":
              this.groups = [
                {
                  label: "1. Obrazovanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g15_a01"
                },
                {
                  label: "2. Kultura, nauka, omladina, sport",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g15_a02"
                },
                {
                  label: "3. Informisanje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g15_a03"
                }
              ];
              break;
            case "XVI	SOCIJALNA POLITIKA I ZAŠTITA ZDRAVLJA":
              this.groups = [
                {
                  label: "1. Socijalno osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a01"
                },
                {
                  label: "2. Doprinosi za obavezno socijalno osiguranje",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a02"
                },
                {
                  label: "3. Socijalna zaštita i društvena briga o deci",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a03"
                },
                {
                  label: "4. Boračka zaštita",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a04"
                },
                {
                  label: "5. Humanitarne organizacije",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a05"
                },
                {
                  label: "6. Proizvodnja i promet lekova i opojnih droga",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g16_a06"
                }
              ];
              break;
            case "XVII	OSTALI MEĐUNARODNI UGOVORI":
              this.groups = [
                {
                  label: "1. Propisi koji su vremenski ograničeni",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g17_a01"
                },
                {
                  label: "2. Ostali međunarodni ugovori",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g17_a02"
                },
                {
                  label: "3. Drugi akti",
                  value:
                    "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#s03_g17_a03"
                }
              ];
              break;
          }
          break;
      }
    }
  }
};
</script>
