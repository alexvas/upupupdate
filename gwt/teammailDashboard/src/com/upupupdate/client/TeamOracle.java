package com.upupupdate.client;

import com.google.gwt.user.client.ui.MultiWordSuggestOracle;
import com.upupupdate.client.jso.DataSource;

public class TeamOracle extends MultiWordSuggestOracle {
    public TeamOracle(String teamName) {
        super("\"., <>@");
        addAll(DataSource.INSTANCE.getTeams().get(teamName));
    }    
}
