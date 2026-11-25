package ai.trustlens.mobile;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TrustLensSecureStoragePlugin.class);
        registerPlugin(TrustLensShareIntentPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
