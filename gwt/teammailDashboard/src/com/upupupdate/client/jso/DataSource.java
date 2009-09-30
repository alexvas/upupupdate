package com.upupupdate.client.jso;

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

public enum DataSource {
    INSTANCE;
    
    private Map<String, String> users = null;

    private Map<String, Set<String>> teams = null;

    public Map<String, String> getUsers() {
        if (users != null) {
            return users;
        }
        users = new LinkedHashMap<String, String>();
        EmbeddedArray keys = getEmbeddedArray("user_keys");
        EmbeddedArray values = getEmbeddedArray("user_values");

        for (int i = 0, n = keys.length(); i < n; ++i) {
            users.put(keys.get(i), values.get(i));
        }

        return users;
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
                members.add(getUsers().get(teamContactKey));
            }
            Set<String> complement = new LinkedHashSet<String>(getUsers().values());
            complement.removeAll(members);
            teams.put(name, complement);
        }
        
        return teams;        
    }
    
    private final native EmbeddedArray getEmbeddedArray(String name) /*-{
        return $wnd[name];
    }-*/;
}
