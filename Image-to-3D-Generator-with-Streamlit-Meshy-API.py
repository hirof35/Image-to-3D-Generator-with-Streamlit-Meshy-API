import streamlit as st
import httpx
import time

# --- 設定 ---
MESHY_API_KEY = "あなたのAPIキー" 

st.title("🚀 3D生成 & ダウンロード")

uploaded_file = st.file_uploader("画像を選択してください", type=['png', 'jpg', 'jpeg'])

if uploaded_file and st.button("3D生成を開始"):
    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
    st.write("🔄 タスクを送信中...")
    
    with httpx.Client() as client:
        try:
            # 1. 生成タスクの作成
            files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = client.post(
                "https://api.meshy.ai/v1/image-to-3d",
                headers=headers,
                files=files,
                data={"enable_pbr": "true"},
                timeout=30.0
            )
            
            if response.status_code not in [200, 202]:
                st.error("APIエラーが発生しました。")
                st.json(response.json())
            else:
                task_id = response.json().get("result")
                st.success(f"タスク開始！ ID: {task_id}")
                
                # 2. 進捗監視
                status_area = st.empty()
                while True:
                    res = client.get(
                        f"https://api.meshy.ai/v1/image-to-3d/{task_id}",
                        headers=headers
                    )
                    data = res.json()
                    status = data.get("status")
                    progress = data.get("progress", 0)
                    
                    status_area.info(f"進捗: {progress}% (ステータス: {status})")
                    
                    if status == "SUCCEEDED":
                        st.success("✅ 生成完了！")
                        glb_url = data.get('model_urls', {}).get('glb')
                        
                        # 3. GLBファイルの取得（ダウンロード準備）
                        st.write("📥 ファイルを準備しています...")
                        glb_content = client.get(glb_url).content
                        
                        st.divider()
                        # 4. ダウンロードボタンの表示
                        st.download_button(
                            label="📥 3Dモデル(.glb)を保存する",
                            data=glb_content,
                            file_name=f"mesh_{int(time.time())}.glb",
                            mime="model/gltf-binary"
                        )
                        st.balloons() # お祝いの演出
                        break
                        
                    elif status == "FAILED":
                        st.error("生成に失敗しました。")
                        break
                    
                    time.sleep(5)
                    
        except Exception as e:
            st.error(f"実行中にエラーが発生しました: {str(e)}")
