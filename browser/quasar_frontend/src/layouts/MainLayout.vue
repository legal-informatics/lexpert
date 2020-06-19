<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
          Servis za pretraživanje pravnih propisa Republike Srbije
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
    >
      <q-list>
        <q-item-label header class="text-grey-8">
          Meni
        </q-item-label>
        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import EssentialLink from "components/EssentialLink";

export default {
  name: "MainLayout",

  components: {
    EssentialLink
  },

  data() {
    return {
      leftDrawerOpen: false,
      essentialLinks: [
        {
          title: "Početna stranica",
          caption: "Početna stranica",
          icon: "home",
          link: "/#"
        },
        {
          title: "Osnovna pretraga",
          caption: "Osnovna pretraga",
          icon: "search",
          link: "/#/osnovna-pretraga"
        },
        {
          title: "Napredna pretraga",
          caption: "Napredna pretraga",
          icon: "img:statics/icon-owl.png",
          link: "/#/napredna-pretraga"
        },
        {
          title: "Dodavanje dokumenata",
          caption: "Dodavanje dokumenata",
          icon: "note_add",
          link: "/#/dodavanje"
        },
        {
          title: "Uklanjanje dokumenata",
          caption: "Uklanjanje dokumenata",
          icon: "delete",
          link: "/#/uklanjanje"
        },
        {
          title: "Izmena dokumenata",
          caption: "Izmena dokumenata",
          icon: "edit",
          link: "/#/izmena"
        }
      ]
    };
  }
};
</script>
