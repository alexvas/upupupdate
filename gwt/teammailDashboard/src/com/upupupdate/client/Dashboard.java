package com.upupupdate.client;

import java.util.Set;

import com.allen_sauer.gwt.log.client.Log;
import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Element;
import com.google.gwt.event.dom.client.HandlesAllKeyEvents;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DeferredCommand;
import com.google.gwt.user.client.ui.SuggestBox;
import com.upupupdate.client.jso.DataSource;

public class Dashboard implements EntryPoint {
    public void onModuleLoad() {
        Log.setUncaughtExceptionHandler();

        DeferredCommand.addCommand(new Command() {
            public void execute() {
                onModuleLoad2();
            }
        });
    }

    public void onModuleLoad2() {
        Set<String> teamNames = DataSource.INSTANCE.getTeams().keySet();

        int i = 0;
        for (String teamName : teamNames) {
            Element input = Document.get().getElementById("team_" + i);
            ++i;
            if (input == null) {
                continue;
            }
            SuggestBox box = SuggestBox.wrap(new TeamOracle(teamName), input);
            new EnterStopper(box).addKeyHandlersTo(box);
        }
    }

    static class EnterStopper extends HandlesAllKeyEvents implements
            ValueChangeHandler<String> {

        private final SuggestBox box;

        private EnterStopper(SuggestBox box) {
            this.box = box;
        }

        public void onKeyDown(KeyDownEvent event) {
            if (box.isSuggestionListShowing()
                    && KeyCodes.KEY_ENTER == event.getNativeKeyCode()) {
                event.stopPropagation();
                event.preventDefault();
            }
        }

        @Override
        public void onValueChange(ValueChangeEvent<String> event) {
            // do nothing
        }

        @Override
        public void onKeyUp(KeyUpEvent event) {
            if (box.isSuggestionListShowing()
                    && KeyCodes.KEY_ENTER == event.getNativeKeyCode()) {
                event.stopPropagation();
                event.preventDefault();
            }
        }

        @Override
        public void onKeyPress(KeyPressEvent event) {
            // do nothing
        }
    }
}
