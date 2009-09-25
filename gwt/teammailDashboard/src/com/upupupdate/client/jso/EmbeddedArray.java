package com.upupupdate.client.jso;

import com.google.gwt.core.client.JavaScriptObject;

public class EmbeddedArray extends JavaScriptObject {
    protected EmbeddedArray() {};
    
    public final native int length() /*-{ return this.length; }-*/;
    public final native String get(int i) /*-{ return this[i];     }-*/;
}
