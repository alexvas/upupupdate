package com.upupupdate.client.jso;

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

public enum DataSource {
    INSTANCE;
    
    private Map<String, String> contacts = null;

    private Map<String, Set<String>> teams = null;

    public Map<String, String> getContacts() {
        if (contacts != null) {
            return contacts;
        }
        contacts = new LinkedHashMap<String, String>();
        EmbeddedArray keys = getEmbeddedArray("contact_keys");
        EmbeddedArray values = getEmbeddedArray("contact_values");

        for (int i = 0, n = keys.length(); i < n; ++i) {
            contacts.put(keys.get(i), values.get(i));
        }

        return contacts;
    }

    public Map<String, Set<String>> getTeams() {
        if (teams != null) {
            return teams;
        }
        teams = new LinkedHashMap<String, Set<String>>();
        EmbeddedArray names = getEmbeddedArray("teams");
        
        for (int i = 0, n = names.length(); i < n; ++i) {
            String name = names.get(i);
            EmbeddedArray teamContactKeys = getEmbeddedArray("team_" + i);
            Set<String> members = new HashSet<String>();
            for (int j = 0, m = teamContactKeys.length(); j < m; ++j) {
                String teamContactKey = teamContactKeys.get(j);
                members.add(getContacts().get(teamContactKey));
            }
            Set<String> complement = new LinkedHashSet<String>(getContacts().values());
            complement.removeAll(members);
            teams.put(name, complement);
        }
        
        return teams;        
    }
    
    private final native EmbeddedArray getEmbeddedArray(String name) /*-{
        return $wnd[name];
    }-*/;
}
