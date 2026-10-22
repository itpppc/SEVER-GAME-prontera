package th.prontera.lanka;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Full-screen WebView around the web game, so updates on the website reach players without a reinstall. */
public class MainActivity extends Activity {
    private static final String HOST = "sever-game-prontera.vercel.app";
    private static final String START = "https://" + HOST + "/rpg?source=apk";
    private static final String OFFLINE =
        "<html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head>"
        + "<body style='margin:0;background:#160f24;color:#f6f0ff;font-family:sans-serif;display:flex;"
        + "align-items:center;justify-content:center;height:100vh;text-align:center'><div>"
        + "<h2 style='color:#f2c14e'>ยังไม่ได้ต่ออินเทอร์เน็ต</h2>"
        + "<p>เปิด Wi-Fi หรือเน็ตมือถือ แล้วกดปุ่มด้านล่าง</p>"
        + "<p><a href='" + START + "' style='display:inline-block;padding:12px 24px;border-radius:99px;"
        + "background:#f2c14e;color:#2b1b05;font-weight:bold;text-decoration:none'>ลองใหม่</a></p>"
        + "</div></body></html>";

    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(0x16, 0x0f, 0x24));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                Uri uri = Uri.parse(url);
                if (HOST.equals(uri.getHost())) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception ignored) {
                    // no app can open this link; stay in the game
                }
                return true;
            }

            @Override
            public void onReceivedError(WebView view, int code, String description, String failingUrl) {
                view.loadDataWithBaseURL(START, OFFLINE, "text/html", "utf-8", null);
            }
        });
        setContentView(web);
        if (state == null || web.restoreState(state) == null) web.loadUrl(START);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onPause() {
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }
}
