/**
 * Victoria International College - Admin Dashboard Controller
 * Handles user management, SQLite DB data operations, OpenAI API key configuration, and chat logs.
 */

(function() {
  'use strict';

  let currentAdminUser = null;
  let allUsers = [];
  let allChatLogs = [];
  let allArticles = [];
  let currentPreviewArticle = null;

  const fetchApi = (url, opts) => {
    const finalUrl = typeof window.getVicApiUrl === 'function' ? window.getVicApiUrl(url) : url;
    return fetch(finalUrl, opts);
  };

  const AdminApp = {
    async init() {
      this.bindTabNavigation();
      this.bindFormEvents();
      await this.checkAuthStatus();
    },

    async checkAuthStatus() {
      const token = window.VicAuth?.getToken();
      const loginGuard = document.getElementById('admin-login-guard');
      const dashboardView = document.getElementById('admin-dashboard-view');
      const adminUserInfo = document.getElementById('admin-user-info');

      if (!token) {
        if (loginGuard) loginGuard.style.display = 'block';
        if (dashboardView) dashboardView.style.display = 'none';
        return;
      }

      try {
        const res = await fetchApi('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await this.safeJson(res);

        if (data.authenticated && data.user && data.user.role === 'admin') {
          currentAdminUser = data.user;
          if (loginGuard) loginGuard.style.display = 'none';
          if (dashboardView) dashboardView.style.display = 'block';

          const isSuperAdmin = currentAdminUser.is_super_admin || currentAdminUser.email === 'mack.chen@viccollege.com' || currentAdminUser.email === 'admin@viccollege.com';
          const roleBadge = isSuperAdmin
            ? '<span class="badge-role admin" style="background:#dc2626; margin-left: 5px;">SUPER ADMIN</span>'
            : '<span class="badge-role admin" style="margin-left: 5px;">ADMIN</span>';

          if (adminUserInfo) {
            adminUserInfo.innerHTML = `
              <div class="user-cell">
                <img src="${currentAdminUser.avatar_url}" alt="${currentAdminUser.name}" class="user-avatar-sm">
                <div>
                  <strong>${currentAdminUser.name}</strong>
                  ${roleBadge}
                </div>
                <button type="button" class="btn-admin-secondary js-admin-logout" style="margin-left: 10px; padding: 4px 8px; font-size: 11px;">
                  <i class="fa-solid fa-power-off"></i> Logout
                </button>
              </div>
            `;
            const logoutBtn = adminUserInfo.querySelector('.js-admin-logout');
            if (logoutBtn) logoutBtn.onclick = () => window.VicAuth.logout();
          }

          // Load data
          this.loadStats();
          this.loadUsers();
          this.loadKnowledge();
          this.loadSEOArticles();
          this.loadAISettings();
          this.loadChatLogs();

          // Check URL query parameters or hash to jump straight to a tab
          const urlParams = new URLSearchParams(window.location.search);
          const targetTab = urlParams.get('tab') || (window.location.hash ? window.location.hash.replace('#', '').replace('tab-', '') : null);

          if (targetTab && document.getElementById(`tab-${targetTab}`)) {
            this.switchTab(targetTab);
          }
        } else {
          if (loginGuard) loginGuard.style.display = 'block';
          if (dashboardView) dashboardView.style.display = 'none';
          if (data.user) {
            this.showToast('Access denied. Administrator privileges required.', 'error');
          }
        }
      } catch (err) {
        if (loginGuard) loginGuard.style.display = 'block';
        if (dashboardView) dashboardView.style.display = 'none';
      }
    },

    switchTab(tabId) {
      document.querySelectorAll('.admin-tab-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.tab === tabId);
      });
      document.querySelectorAll('.admin-tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `tab-${tabId}`);
      });

      if (tabId === 'overview') this.loadStats();
      if (tabId === 'users') this.loadUsers();
      if (tabId === 'knowledge') this.loadKnowledge();
      if (tabId === 'seo-articles') this.loadSEOArticles();
      if (tabId === 'ai-settings') this.loadAISettings();
      if (tabId === 'chat-logs') this.loadChatLogs();
    },

    bindTabNavigation() {
      document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.switchTab(btn.dataset.tab);
        });
      });
    },

    bindFormEvents() {
      // 1. Guard Login Form
      const guardForm = document.getElementById('guard-login-form');
      if (guardForm) {
        guardForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const email = document.getElementById('guard-email').value;
          const password = document.getElementById('guard-password').value;
          try {
            await window.VicAuth.login(email, password);
            await this.checkAuthStatus();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      // 1b. Guard Google Login Button
      const adminGoogleBtn = document.getElementById('admin-google-btn');
      if (adminGoogleBtn) {
        adminGoogleBtn.addEventListener('click', async () => {
          try {
            await window.VicAuth.loginWithGoogle('mack.chen@viccollege.com', 'Mack Chen (Super Admin)');
            await this.checkAuthStatus();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      // 2. User Search & Filter
      const searchInput = document.getElementById('user-search-input');
      const roleFilter = document.getElementById('user-role-filter');
      const providerFilter = document.getElementById('user-provider-filter');

      const applyFilters = () => {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const role = roleFilter ? roleFilter.value : '';
        const provider = providerFilter ? providerFilter.value : '';

        const filtered = allUsers.filter(u => {
          const matchQuery = !query || u.name.toLowerCase().includes(query) || u.email.toLowerCase().includes(query);
          const matchRole = !role || u.role === role;
          const matchProvider = !provider || u.provider === provider;
          return matchQuery && matchRole && matchProvider;
        });

        this.renderUsersTable(filtered);
      };

      if (searchInput) searchInput.addEventListener('input', applyFilters);
      if (roleFilter) roleFilter.addEventListener('change', applyFilters);
      if (providerFilter) providerFilter.addEventListener('change', applyFilters);

      // 3. Add User Modal
      const openAddModalBtn = document.querySelector('.js-open-add-user-modal');
      const closeAddModalBtns = document.querySelectorAll('.js-close-add-user-modal');
      const addModal = document.getElementById('modal-add-user');

      if (openAddModalBtn && addModal) {
        openAddModalBtn.onclick = () => addModal.classList.add('active');
      }
      closeAddModalBtns.forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          if (addModal) addModal.classList.remove('active');
        };
      });

      const addUserForm = document.getElementById('form-admin-add-user');
      if (addUserForm) {
        addUserForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const name = document.getElementById('new-user-name').value;
          const email = document.getElementById('new-user-email').value;
          const password = document.getElementById('new-user-password').value;
          const role = document.getElementById('new-user-role').value;

          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/admin/users', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ name, email, password, role })
            });
            const data = await this.safeJson(res);
            if (!res.ok) throw new Error(data.error || 'Failed to create user');

            this.showToast('User account created successfully!', 'success');
            if (addModal) addModal.classList.remove('active');
            addUserForm.reset();
            this.loadUsers();
            this.loadStats();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      // 3b. Knowledge Base Modal & Filters
      const openAddKbBtn = document.querySelector('.js-open-add-kb-modal');
      const closeKbModalBtns = document.querySelectorAll('.js-close-kb-modal');
      const kbModal = document.getElementById('modal-kb-editor');
      const kbForm = document.getElementById('form-admin-kb-editor');

      if (openAddKbBtn && kbModal) {
        openAddKbBtn.onclick = () => {
          document.getElementById('kb-edit-id').value = '';
          document.getElementById('kb-modal-title').textContent = 'Add Knowledge Base Article';
          document.getElementById('kb-modal-submit-btn').textContent = 'Save Article to Knowledge Base';
          if (kbForm) kbForm.reset();
          kbModal.classList.add('active');
        };
      }

      closeKbModalBtns.forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          if (kbModal) kbModal.classList.remove('active');
        };
      });

      if (kbForm) {
        kbForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const editId = document.getElementById('kb-edit-id').value;
          const title = document.getElementById('kb-input-title').value.trim();
          const category = document.getElementById('kb-input-category').value;
          const priority = document.getElementById('kb-input-priority').value;
          const keywords = document.getElementById('kb-input-keywords').value.trim();
          const content = document.getElementById('kb-input-content').value.trim();

          try {
            const token = window.VicAuth.getToken();
            const method = editId ? 'PUT' : 'POST';
            const url = editId ? `/api/admin/knowledge/${editId}` : '/api/admin/knowledge';

            const res = await fetchApi(url, {
              method,
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ title, category, priority, keywords, content })
            });
            const data = await this.safeJson(res);
            if (!res.ok) throw new Error(data.error || 'Failed to save knowledge article');

            this.showToast(data.message || 'Knowledge article saved successfully!', 'success');
            if (kbModal) kbModal.classList.remove('active');
            kbForm.reset();
            this.loadKnowledge();
            this.loadStats();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      const kbSearchInput = document.getElementById('kb-search-input');
      const kbCategoryFilter = document.getElementById('kb-category-filter');
      if (kbSearchInput) {
        kbSearchInput.addEventListener('input', () => this.loadKnowledge());
      }
      if (kbCategoryFilter) {
        kbCategoryFilter.addEventListener('change', () => this.loadKnowledge());
      }

      // Universal Backdrop click to close modals
      document.querySelectorAll('.vic-auth-modal-backdrop').forEach(modalBackdrop => {
        modalBackdrop.addEventListener('click', (e) => {
          if (e.target === modalBackdrop) {
            modalBackdrop.classList.remove('active');
          }
        });
      });

      // Escape key to close active modals
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          document.querySelectorAll('.vic-auth-modal-backdrop.active').forEach(m => m.classList.remove('active'));
        }
      });

      // 3c. Knowledge Base Query Tester
      const openTestKbBtn = document.querySelector('.js-open-test-kb-modal');
      const closeTestKbBtn = document.querySelector('.js-close-kb-test-modal');
      const testKbModal = document.getElementById('modal-kb-tester');
      const testKbForm = document.getElementById('form-test-kb-query');

      if (openTestKbBtn && testKbModal) {
        openTestKbBtn.onclick = () => {
          testKbModal.classList.add('active');
        };
      }

      if (closeTestKbBtn && testKbModal) {
        closeTestKbBtn.onclick = () => testKbModal.classList.remove('active');
      }

      if (testKbForm) {
        testKbForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const query = document.getElementById('kb-test-input-query').value.trim();
          const resultsContainer = document.getElementById('kb-test-results-container');
          if (!query || !resultsContainer) return;

          resultsContainer.style.display = 'block';
          resultsContainer.innerHTML = '<div style="text-align:center; padding:20px;"><i class="fa-solid fa-spinner fa-spin"></i> Searching knowledge base database...</div>';

          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/admin/knowledge/test-query', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ query })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Test search failed');

            const isDirectHit = data.top_score >= 0.70;
            const isRagHit = data.top_score >= 0.15 && !isDirectHit;

            resultsContainer.innerHTML = `
              <div style="background:#f8f9fa; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                  <strong style="color:#1e293b;">Routing Decision:</strong>
                  <span style="font-weight:700; font-size:13px; padding:4px 10px; border-radius:20px; ${isDirectHit ? 'background:#dcfce7; color:#15803d;' : isRagHit ? 'background:#e0e7ff; color:#4338ca;' : 'background:#fee2e2; color:#b91c1c;'}">
                    ${isDirectHit ? '⚡ DIRECT LOCAL KB HIT (100% Match)' : isRagHit ? '🧠 OPENAI RAG SYNTHESIS' : '❓ GENERAL AI / FALLBACK'}
                  </span>
                </div>
                <p style="font-size:13.5px; color:#475569; margin:0;">
                  <strong>Action:</strong> <code>${data.action_preview}</code><br>
                  <strong>Top Confidence Score:</strong> ${(data.top_score * 100).toFixed(1)}%
                </p>
              </div>

              <h4 style="font-size:14px; margin-bottom:10px; color:#333;">Top Retrieved Knowledge Matches (${data.matches.length}):</h4>
              ${data.matches.length === 0 ? '<p style="color:#888;">No matching knowledge base documents found.</p>' : data.matches.map((m, idx) => `
                <div style="border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:10px; background:#fff;">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                    <div>
                      <span style="font-size:11px; font-weight:700; text-transform:uppercase; color:#B72425; background:#fff1f2; padding:2px 6px; border-radius:4px;">${m.category}</span>
                      <strong style="margin-left:6px; font-size:14px; color:#1e293b;">#${idx+1} ${m.title}</strong>
                    </div>
                    <span style="font-size:13px; font-weight:700; color:${m.score >= 0.7 ? '#16a34a' : m.score >= 0.3 ? '#2563eb' : '#d97706'};">
                      Score: ${(m.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p style="font-size:12.5px; color:#64748b; margin-bottom:6px;"><strong>Keywords:</strong> ${m.keywords}</p>
                  <p style="font-size:13px; color:#334155; line-height:1.45; background:#f8fafc; padding:8px 10px; border-radius:6px; border-left:3px solid #cbd5e1; margin:0;">
                    ${m.content}
                  </p>
                </div>
              `).join('')}
            `;
          } catch (err) {
            resultsContainer.innerHTML = `<div style="color:red; padding:15px;">Error: ${err.message}</div>`;
          }
        });
      }

      // 3d. SEO & GEO Article Generator
      const genArticleForm = document.getElementById('form-generate-seo-article');
      if (genArticleForm) {
        genArticleForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const keywords = document.getElementById('seo-gen-keywords').value.trim();
          const geo_target = document.getElementById('seo-gen-geo').value;
          const category = document.getElementById('seo-gen-category').value;
          const language = document.getElementById('seo-gen-language').value;
          const tone = document.getElementById('seo-gen-tone').value;
          const genBtn = document.getElementById('btn-generate-seo-art');

          if (!keywords) {
            this.showToast('Please enter target keywords for article generation', 'warning');
            return;
          }

          const originalBtnHtml = genBtn.innerHTML;
          genBtn.disabled = true;
          genBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating SEO Article...';

          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/admin/articles/generate', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ keywords, geo_target, category, language, tone })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to generate SEO article');

            this.showToast(data.message || 'Article generated successfully (Hidden by default)!', 'success');
            genArticleForm.reset();
            this.loadSEOArticles();
            this.loadStats();
          } catch (err) {
            this.showToast(err.message, 'error');
          } finally {
            genBtn.disabled = false;
            genBtn.innerHTML = originalBtnHtml;
          }
        });
      }

      // 3e. SEO Article Editor Modal & Manual Create
      const openAddArtBtn = document.querySelector('.js-open-add-article-modal');
      const closeArtModalBtns = document.querySelectorAll('.js-close-art-modal');
      const artModal = document.getElementById('modal-article-editor');
      const artForm = document.getElementById('form-admin-article-editor');

      if (openAddArtBtn) {
        openAddArtBtn.onclick = () => this.openArticleEditor();
      }

      closeArtModalBtns.forEach(btn => {
        btn.onclick = () => {
          if (artModal) artModal.classList.remove('active');
        };
      });

      if (artForm) {
        artForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const editId = document.getElementById('art-edit-id').value;
          const title = document.getElementById('art-input-title').value.trim();
          const slug = document.getElementById('art-input-slug').value.trim();
          const geo_target = document.getElementById('art-input-geo').value.trim();
          const category = document.getElementById('art-input-category').value;
          const status = document.getElementById('art-input-status').value;
          const keywords = document.getElementById('art-input-keywords').value.trim();
          const summary = document.getElementById('art-input-summary').value.trim();
          const content = document.getElementById('art-input-content').value.trim();

          try {
            const token = window.VicAuth.getToken();
            const method = editId ? 'PUT' : 'POST';
            const url = editId ? `/api/admin/articles/${editId}` : '/api/admin/articles';

            const res = await fetchApi(url, {
              method,
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ title, slug, geo_target, category, status, keywords, summary, content })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to save article');

            this.showToast(data.message || 'Article saved successfully!', 'success');
            if (artModal) artModal.classList.remove('active');
            artForm.reset();
            this.loadSEOArticles();
            this.loadStats();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      // 3f. SEO Preview Modal & Publish Toggle
      const closePreviewBtns = document.querySelectorAll('.js-close-art-preview-modal');
      const previewModal = document.getElementById('modal-article-preview');
      const previewToggleBtn = document.getElementById('btn-preview-toggle-publish');

      closePreviewBtns.forEach(btn => {
        btn.onclick = () => {
          if (previewModal) previewModal.classList.remove('active');
        };
      });

      if (previewToggleBtn) {
        previewToggleBtn.onclick = async () => {
          if (!currentPreviewArticle) return;
          await this.toggleArticleStatus(currentPreviewArticle.id);
          if (previewModal) previewModal.classList.remove('active');
        };
      }

      // 3g. Sitemap Management Handlers
      const syncSitemapBtn = document.querySelector('.js-sync-sitemap');
      if (syncSitemapBtn) {
        syncSitemapBtn.onclick = () => this.syncSitemap();
      }

      const copySitemapUrlBtn = document.querySelector('.js-copy-sitemap-url');
      if (copySitemapUrlBtn) {
        copySitemapUrlBtn.onclick = () => {
          const sitemapUrl = window.location.origin + '/sitemap.xml';
          navigator.clipboard.writeText(sitemapUrl).then(() => {
            this.showToast('Copied sitemap URL to clipboard: ' + sitemapUrl, 'success');
          }).catch(() => {
            prompt('Copy Sitemap URL:', sitemapUrl);
          });
        };
      }

      const inspectSitemapBtn = document.querySelector('.js-inspect-sitemap');
      const closeSitemapModalBtns = document.querySelectorAll('.js-close-sitemap-modal');
      const sitemapModal = document.getElementById('modal-sitemap-viewer');
      const copyXmlBtn = document.querySelector('.js-copy-xml-btn');

      if (inspectSitemapBtn) {
        inspectSitemapBtn.onclick = () => this.inspectSitemap();
      }
      closeSitemapModalBtns.forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          if (sitemapModal) sitemapModal.classList.remove('active');
        };
      });
      if (copyXmlBtn) {
        copyXmlBtn.onclick = () => {
          const xmlPre = document.getElementById('sitemap-xml-pre');
          if (xmlPre) {
            navigator.clipboard.writeText(xmlPre.textContent).then(() => {
              this.showToast('Copied raw XML sitemap to clipboard!', 'success');
            });
          }
        };
      }

      // 3h. Article Search & Filters
      const artSearchInput = document.getElementById('art-search-input');
      const artStatusFilter = document.getElementById('art-status-filter');
      const artCategoryFilter = document.getElementById('art-category-filter');

      if (artSearchInput) artSearchInput.addEventListener('input', () => this.loadSEOArticles());
      if (artStatusFilter) artStatusFilter.addEventListener('change', () => this.loadSEOArticles());
      if (artCategoryFilter) artCategoryFilter.addEventListener('change', () => this.loadSEOArticles());

      // 4. OpenAI Settings Form
      const aiForm = document.getElementById('ai-settings-form');
      if (aiForm) {
        aiForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const keyInput = document.getElementById('set-openai-key').value;
          const model = document.getElementById('set-openai-model').value;
          const temp = document.getElementById('set-temperature').value;
          const tokens = document.getElementById('set-max-tokens').value;
          const reqLogin = document.getElementById('set-require-login').value;
          const prompt = document.getElementById('set-system-prompt').value;

          try {
            const token = window.VicAuth.getToken();
            const payload = {
              openai_model: model,
              temperature: temp,
              max_tokens: tokens,
              require_login: reqLogin,
              system_prompt: prompt
            };
            if (keyInput && !keyInput.includes('••••')) {
              payload.openai_api_key = keyInput.trim();
            }

            const res = await fetchApi('/api/admin/settings', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to save settings');

            this.showToast('OpenAI configuration saved to database!', 'success');
            this.loadAISettings();
            this.loadStats();
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        });
      }

      // 5. Test Key Connection Button
      const testKeyBtn = document.querySelector('.js-test-api-key');
      const toggleKeyBtn = document.querySelector('.js-toggle-key-visibility');
      const keyInput = document.getElementById('set-openai-key');

      if (toggleKeyBtn && keyInput) {
        toggleKeyBtn.onclick = () => {
          keyInput.type = keyInput.type === 'password' ? 'text' : 'password';
          toggleKeyBtn.innerHTML = keyInput.type === 'password' ? '<i class="fa-solid fa-eye"></i>' : '<i class="fa-solid fa-eye-slash"></i>';
        };
      }

      if (testKeyBtn) {
        testKeyBtn.addEventListener('click', async () => {
          const testBox = document.getElementById('api-key-test-result');
          const keyVal = document.getElementById('set-openai-key').value;

          if (testBox) {
            testBox.style.display = 'block';
            testBox.className = 'test-feedback-box';
            testBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing connection to OpenAI API...';
          }

          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/admin/settings/test-key', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ openai_api_key: keyVal })
            });
            const data = await res.json();

            if (testBox) {
              if (res.ok && data.valid) {
                testBox.className = 'test-feedback-box success';
                testBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message}`;
              } else {
                testBox.className = 'test-feedback-box error';
                testBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${data.message || 'Key validation failed.'}`;
              }
            }
          } catch (err) {
            if (testBox) {
              testBox.className = 'test-feedback-box error';
              testBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Network error: ${err.message}`;
            }
          }
        });
      }

      // 5b. Change Password Form
      const changePwdForm = document.getElementById('form-change-password');
      if (changePwdForm) {
        changePwdForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const oldPwd = document.getElementById('pwd-current').value;
          const newPwd = document.getElementById('pwd-new').value;
          const confirmPwd = document.getElementById('pwd-confirm').value;
          const msgBox = document.getElementById('pwd-change-msg');

          if (newPwd !== confirmPwd) {
            if (msgBox) {
              msgBox.style.display = 'block';
              msgBox.className = 'test-feedback-box error';
              msgBox.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> New passwords do not match.';
            }
            return;
          }

          if (msgBox) {
            msgBox.style.display = 'block';
            msgBox.className = 'test-feedback-box';
            msgBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating password in database...';
          }

          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/auth/change-password', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
            });
            const data = await res.json();

            if (msgBox) {
              if (res.ok) {
                msgBox.className = 'test-feedback-box success';
                msgBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message || 'Password updated successfully in database!'}`;
                changePwdForm.reset();
                this.showToast('Password changed successfully!', 'success');
              } else {
                msgBox.className = 'test-feedback-box error';
                msgBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${data.error || 'Failed to update password.'}`;
              }
            }
          } catch (err) {
            if (msgBox) {
              msgBox.className = 'test-feedback-box error';
              msgBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Network error: ${err.message}`;
            }
          }
        });
      }

      // 6. Clear Logs Button
      const clearLogsBtn = document.querySelector('.js-clear-logs');
      if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', async () => {
          if (!confirm("Are you sure you want to clear all conversation logs?")) return;
          try {
            const token = window.VicAuth.getToken();
            const res = await fetchApi('/api/admin/logs', {
              method: 'DELETE',
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
              this.showToast('Conversation logs cleared.', 'info');
              this.loadChatLogs();
              this.loadStats();
            }
          } catch (e) {
            this.showToast('Failed to clear logs', 'error');
          }
        });
      }

      // 7. Conversation Logs Search Filter
      const logsSearchInput = document.getElementById('logs-search-input');
      if (logsSearchInput) {
        logsSearchInput.addEventListener('input', () => {
          const q = logsSearchInput.value.toLowerCase().trim();
          if (!q) {
            this.renderChatLogsTable(allChatLogs);
          } else {
            const filtered = allChatLogs.filter(l => 
              (l.query && l.query.toLowerCase().includes(q)) ||
              (l.response && l.response.toLowerCase().includes(q)) ||
              (l.user_name && l.user_name.toLowerCase().includes(q)) ||
              (l.model && l.model.toLowerCase().includes(q))
            );
            this.renderChatLogsTable(filtered);
          }
        });
      }
    },

    // Load Overview Statistics
    async loadStats() {
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi('/api/admin/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          document.getElementById('stat-total-users').textContent = data.total_users || 0;
          const kbStatEl = document.getElementById('stat-kb-articles');
          if (kbStatEl) kbStatEl.textContent = data.knowledge_articles || 0;
          const totalArtEl = document.getElementById('stat-total-articles');
          if (totalArtEl) totalArtEl.textContent = data.total_articles || 0;
          const activeArtEl = document.getElementById('stat-active-articles');
          if (activeArtEl) activeArtEl.textContent = data.active_articles || 0;
          const sitemapUrlsEl = document.getElementById('stat-sitemap-urls');
          if (sitemapUrlsEl) sitemapUrlsEl.textContent = data.sitemap_urls || 5;
          document.getElementById('stat-google-users').textContent = data.google_users || 0;
          document.getElementById('stat-linkedin-users').textContent = data.linkedin_users || 0;
          document.getElementById('stat-total-chats').textContent = data.total_chats || 0;
          document.getElementById('stat-key-status').innerHTML = data.has_api_key 
            ? '<span style="color:#059669; font-size: 16px;">Active (In DB)</span>' 
            : '<span style="color:#DC2626; font-size: 16px;">Not Set</span>';
          const modelEl = document.getElementById('stat-active-model');
          if (modelEl) modelEl.textContent = data.current_model || 'gpt-4o-mini';
        }
      } catch (e) {
        console.warn('Failed to load stats:', e);
      }
    },

    // Load Knowledge Base Articles
    async loadKnowledge() {
      const tbody = document.getElementById('kb-tbody');
      const search = document.getElementById('kb-search-input')?.value || '';
      const category = document.getElementById('kb-category-filter')?.value || 'all';

      try {
        const token = window.VicAuth.getToken();
        const queryParams = new URLSearchParams();
        if (search) queryParams.set('search', search);
        if (category && category !== 'all') queryParams.set('category', category);

        const res = await fetchApi(`/api/admin/knowledge?${queryParams.toString()}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.articles) {
          this.renderKnowledgeTable(data.articles);
        }
      } catch (e) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Failed to load knowledge articles</td></tr>`;
      }
    },

    renderKnowledgeTable(articles) {
      const tbody = document.getElementById('kb-tbody');
      if (!tbody) return;

      if (!articles || articles.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color:#888;">No knowledge articles found. Click "Add Article" to create one.</td></tr>`;
        return;
      }

      const categoryLabels = {
        programs: 'Programs',
        financial_aid: 'Financial Aid',
        admissions: 'Admissions',
        campuses: 'Campuses',
        general: 'General'
      };

      tbody.innerHTML = articles.map(art => {
        const catName = categoryLabels[art.category] || art.category;
        const shortContent = (art.content || '').slice(0, 160) + ((art.content || '').length > 160 ? '...' : '');

        return `
          <tr>
            <td><strong>#${art.id}</strong></td>
            <td>
              <span class="badge-role ${art.category === 'financial_aid' ? 'admin' : 'user'}" style="font-size: 11px;">
                ${catName}
              </span>
            </td>
            <td>
              <strong style="color: #1e293b; font-size: 14px;">${art.title}</strong><br>
              <small style="color: #64748b; display: inline-block; margin-top: 4px;">
                <i class="fa-solid fa-tags" style="color: #94a3b8; font-size: 10px;"></i> ${art.keywords}
              </small>
            </td>
            <td>
              <div style="font-size: 13px; color: #475569; line-height: 1.45; background: #f8fafc; padding: 8px 10px; border-radius: 6px;">
                ${shortContent}
              </div>
            </td>
            <td style="text-align: center;">
              <span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; ${art.priority > 1 ? 'background: #fef3c7; color: #b45309;' : 'background: #f1f5f9; color: #64748b;'}">
                P${art.priority}
              </span>
            </td>
            <td style="text-align: right;">
              <div style="display: flex; gap: 4px; justify-content: flex-end;">
                <button type="button" class="btn-table-action" title="Edit Article" onclick="window.AdminApp.openEditKnowledge(${art.id})">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button type="button" class="btn-table-action delete" title="Delete Article" onclick="window.AdminApp.deleteKnowledge(${art.id})">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    },

    async openEditKnowledge(id) {
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/knowledge/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.article) {
          const art = data.article;
          document.getElementById('kb-edit-id').value = art.id;
          document.getElementById('kb-modal-title').textContent = `Edit Knowledge Article (#${art.id})`;
          document.getElementById('kb-modal-submit-btn').textContent = 'Update Knowledge Article';
          document.getElementById('kb-input-title').value = art.title;
          document.getElementById('kb-input-category').value = art.category;
          document.getElementById('kb-input-priority').value = String(art.priority || 1);
          document.getElementById('kb-input-keywords').value = art.keywords;
          document.getElementById('kb-input-content').value = art.content;

          const modal = document.getElementById('modal-kb-editor');
          if (modal) modal.classList.add('active');
        }
      } catch (e) {
        this.showToast('Failed to fetch article details', 'error');
      }
    },

    async deleteKnowledge(id) {
      if (!confirm('Are you sure you want to permanently delete this knowledge article from the SQLite database?')) return;
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/knowledge/${id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          this.showToast(data.message || 'Knowledge article deleted', 'info');
          this.loadKnowledge();
          this.loadStats();
        }
      } catch (e) {
        this.showToast('Failed to delete knowledge article', 'error');
      }
    },

    // Load Users List
    async loadUsers() {
      const tbody = document.getElementById('users-tbody');
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi('/api/admin/users', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.users) {
          allUsers = data.users;
          this.renderUsersTable(allUsers);
        }
      } catch (e) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Failed to load users</td></tr>`;
      }
    },

    renderUsersTable(users) {
      const tbody = document.getElementById('users-tbody');
      if (!tbody) return;

      if (!users || users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color:#888;">No users found matching query.</td></tr>`;
        return;
      }

      tbody.innerHTML = users.map(u => {
        const joinDate = u.created_at ? new Date(u.created_at).toLocaleDateString() : '--';
        const isSelf = currentAdminUser && currentAdminUser.id === u.id;

        return `
          <tr>
            <td>
              <div class="user-cell">
                <img src="${u.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + u.email}" class="user-avatar-sm" alt="${u.name}">
                <div>
                  <strong>${u.name}</strong>
                  ${isSelf ? '<span style="font-size:10px; color:#B72425; font-weight:bold;">(You)</span>' : ''}
                </div>
              </div>
            </td>
            <td>${u.email}</td>
            <td>
              <span class="badge-provider ${u.provider}">
                <i class="fa-brands ${u.provider === 'google' ? 'fa-google' : u.provider === 'linkedin' ? 'fa-linkedin' : 'fa-envelope'}"></i>
                ${u.provider}
              </span>
            </td>
            <td>
              <span class="badge-role ${u.role}">${u.role.toUpperCase()}</span>
            </td>
            <td>
              <span class="badge-status ${u.status}">${u.status.toUpperCase()}</span>
            </td>
            <td><small>${joinDate}</small></td>
            <td>
              <div style="display:flex; gap: 4px;">
                <button type="button" class="btn-table-action" title="Toggle Role" onclick="window.AdminApp.toggleUserRole(${u.id}, '${u.role}')">
                  <i class="fa-solid fa-user-shield"></i>
                </button>
                <button type="button" class="btn-table-action" title="Toggle Status" onclick="window.AdminApp.toggleUserStatus(${u.id}, '${u.status}')">
                  <i class="fa-solid ${u.status === 'active' ? 'fa-ban' : 'fa-check'}"></i>
                </button>
                ${!isSelf ? `
                  <button type="button" class="btn-table-action delete" title="Delete User" onclick="window.AdminApp.deleteUser(${u.id})">
                    <i class="fa-solid fa-trash-can"></i>
                  </button>
                ` : ''}
              </div>
            </td>
          </tr>
        `;
      }).join('');
    },

    async toggleUserRole(userId, currentRole) {
      const newRole = currentRole === 'admin' ? 'user' : 'admin';
      if (!confirm(`Change this user's role to ${newRole.toUpperCase()}?`)) return;

      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ role: newRole })
        });
        if (res.ok) {
          this.showToast(`User role updated to ${newRole}`, 'success');
          this.loadUsers();
        }
      } catch (e) {
        this.showToast('Failed to update role', 'error');
      }
    },

    async toggleUserStatus(userId, currentStatus) {
      const newStatus = currentStatus === 'active' ? 'suspended' : 'active';
      if (!confirm(`Change this user's status to ${newStatus.toUpperCase()}?`)) return;

      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) {
          this.showToast(`User status updated to ${newStatus}`, 'success');
          this.loadUsers();
        }
      } catch (e) {
        this.showToast('Failed to update status', 'error');
      }
    },

    async deleteUser(userId) {
      if (!confirm('Are you sure you want to permanently delete this user account?')) return;

      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/users/${userId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          this.showToast('User account deleted.', 'info');
          this.loadUsers();
          this.loadStats();
        } else {
          const d = await res.json();
          this.showToast(d.error || 'Failed to delete user', 'error');
        }
      } catch (e) {
        this.showToast('Failed to delete user', 'error');
      }
    },

    // Load AI Settings
    async loadAISettings() {
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi('/api/admin/settings', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();

        if (res.ok) {
          const keyInput = document.getElementById('set-openai-key');
          if (keyInput) keyInput.value = data.openai_api_key_masked || '';

          const modelSelect = document.getElementById('set-openai-model');
          if (modelSelect) modelSelect.value = data.openai_model || 'gpt-4o-mini';

          const tempInput = document.getElementById('set-temperature');
          if (tempInput) tempInput.value = data.temperature || '0.7';

          const tokenInput = document.getElementById('set-max-tokens');
          if (tokenInput) tokenInput.value = data.max_tokens || '800';

          const loginSelect = document.getElementById('set-require-login');
          if (loginSelect) loginSelect.value = String(data.require_login || 'false');

          const promptArea = document.getElementById('set-system-prompt');
          if (promptArea) promptArea.value = data.system_prompt || '';
        }
      } catch (e) {
        console.warn('Failed to load AI settings:', e);
      }
    },

    // Load Chat Logs
    async loadChatLogs() {
      const tbody = document.getElementById('logs-tbody');
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi('/api/admin/logs', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();

        if (res.ok && data.logs) {
          allChatLogs = data.logs;
          this.renderChatLogsTable(allChatLogs);
        }
      } catch (e) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Failed to load chat logs</td></tr>`;
      }
    },

    renderChatLogsTable(logs) {
      const tbody = document.getElementById('logs-tbody');
      if (!tbody) return;

      if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color:#888;">No conversation logs found.</td></tr>`;
        return;
      }

      tbody.innerHTML = logs.map(log => {
        const timeStr = log.created_at ? new Date(log.created_at).toLocaleString() : '--';
        const cleanResponse = (log.response || '').replace(/###/g, '').replace(/\*\*/g, '').slice(0, 160) + ((log.response || '').length > 160 ? '...' : '');
        const isKb = log.model && log.model.includes('knowledge');

        return `
          <tr>
            <td><small style="color: #64748b;">${timeStr}</small></td>
            <td>
              <strong style="color: #1e293b;">${log.user_name || 'Guest Visitor'}</strong><br>
              <small style="color:#888;">${log.user_email || 'No Account'}</small>
            </td>
            <td style="max-width: 250px;">
              <strong style="color: #1e293b; font-size: 13.5px;">${log.query}</strong>
            </td>
            <td style="max-width: 350px;">
              <div style="font-size: 12.5px; color:#475569; line-height: 1.4; background: #f8fafc; padding: 6px 10px; border-radius: 6px; border-left: 2px solid #cbd5e1;">
                ${cleanResponse}
              </div>
            </td>
            <td>
              <span class="badge-provider ${isKb ? 'google' : 'email'}" style="font-size:10.5px; text-transform: none;">
                ${log.model || 'direct'}
              </span>
            </td>
            <td style="text-align: right;">
              <button type="button" class="btn-table-action save-kb" title="Save this Q&A into Knowledge Base" onclick="window.AdminApp.openSaveLogToKnowledge(${log.id})">
                <i class="fa-solid fa-bookmark"></i> Save to KB
              </button>
            </td>
          </tr>
        `;
      }).join('');
    },

    // Save Selected Conversation Log into Knowledge Base
    async openSaveLogToKnowledge(logId) {
      let log = allChatLogs.find(l => l.id === logId);
      if (!log) {
        try {
          const token = window.VicAuth.getToken();
          const res = await fetchApi('/api/admin/logs', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const d = await res.json();
          allChatLogs = d.logs || [];
          log = allChatLogs.find(l => l.id === logId);
        } catch (e) {}
      }

      if (!log) {
        this.showToast('Conversation log record not found', 'error');
        return;
      }

      // Infer appropriate category from query
      let inferredCat = 'general';
      const qLow = log.query.toLowerCase();
      if (['grant', 'second career', 'better job', 'funding', 'aid', '补助', '资助', '免费'].some(k => qLow.includes(k))) {
        inferredCat = 'financial_aid';
      } else if (['psw', 'tech', 'full stack', 'web', 'account', 'tax', 'nurse', 'electrician', 'acupuncture', 'childcare', 'eca', '专业', '课程'].some(k => qLow.includes(k))) {
        inferredCat = 'programs';
      } else if (['campus', 'location', 'address', 'where', 'phone', 'contact', '校区', '地址', '电话', '万锦', '北约克'].some(k => qLow.includes(k))) {
        inferredCat = 'campuses';
      } else if (['admit', 'admission', 'apply', 'enroll', 'tuition', 'fee', 'consult', '报名', '学费', '咨询'].some(k => qLow.includes(k))) {
        inferredCat = 'admissions';
      }

      // Extract keywords from query tokens
      const tokens = log.query
        .toLowerCase()
        .replace(/[^\w\u4e00-\u9fff\s]/g, ' ')
        .split(/\s+/)
        .filter(t => t.length > 1 && !['the', 'is', 'a', 'an', 'how', 'what', 'where', 'when', 'who', 'why', 'can', 'you', 'for', 'in', 'to', 'of', 'and', 'my', 'please', 'tell', 'me'].includes(t));
      const extractedKeywords = tokens.slice(0, 8).join(', ');

      // Prefill Knowledge Base Editor Modal
      document.getElementById('kb-edit-id').value = '';
      document.getElementById('kb-modal-title').textContent = `Save Conversation #${log.id} to Knowledge Base`;
      document.getElementById('kb-modal-submit-btn').textContent = 'Save this Q&A into Knowledge Base';
      document.getElementById('kb-input-title').value = log.query;
      document.getElementById('kb-input-category').value = inferredCat;
      document.getElementById('kb-input-priority').value = '2';
      document.getElementById('kb-input-keywords').value = extractedKeywords || log.query;
      document.getElementById('kb-input-content').value = log.response;

      const modal = document.getElementById('modal-kb-editor');
      if (modal) {
        modal.classList.add('active');
        this.showToast(`Pre-filled Q&A from Log #${log.id}. Review and save!`, 'info');
      }
    },

    // =========================================================================
    // SEO & GEO Articles & Sitemap Management Methods
    // =========================================================================

    async loadSEOArticles() {
      const tbody = document.getElementById('articles-tbody');
      const search = document.getElementById('art-search-input')?.value.trim() || '';
      const status = document.getElementById('art-status-filter')?.value || 'all';
      const category = document.getElementById('art-category-filter')?.value || 'all';

      try {
        const token = window.VicAuth.getToken();
        const queryParams = new URLSearchParams();
        if (search) queryParams.set('search', search);
        if (status && status !== 'all') queryParams.set('status', status);
        if (category && category !== 'all') queryParams.set('category', category);

        const res = await fetchApi(`/api/admin/articles?${queryParams.toString()}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.articles) {
          allArticles = data.articles;
          this.renderArticlesTable(data.articles);

          const badge = document.getElementById('articles-count-badge');
          if (badge && data.stats) {
            badge.textContent = `${data.stats.total} Total (${data.stats.active} Live • ${data.stats.hidden} Hidden Drafts)`;
          }

          const sitemapText = document.getElementById('sitemap-status-text');
          if (sitemapText && data.stats) {
            sitemapText.innerHTML = `<strong>${data.stats.active} active GEO articles</strong> indexed in <code>/sitemap.xml</code> (${5 + data.stats.active} total URLs). Hidden drafts are excluded.`;
          }
        }
      } catch (e) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Failed to load SEO articles</td></tr>`;
      }
    },

    renderArticlesTable(articles) {
      const tbody = document.getElementById('articles-tbody');
      if (!tbody) return;

      if (!articles || articles.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 36px; color:#888;">
          <i class="fa-solid fa-file-circle-question" style="font-size: 28px; margin-bottom: 8px; color: #cbd5e1; display: block;"></i>
          No articles found matching your criteria. Use the AI Generator above to create one based on keywords.
        </td></tr>`;
        return;
      }

      const categoryLabels = {
        healthcare: '🩺 Healthcare (PSW)',
        technology: '💻 Tech & Web',
        financial_aid: '💰 Financial Aid',
        business: '📊 Business & Tax',
        programs: '🎓 Programs'
      };

      tbody.innerHTML = articles.map(art => {
        const isActive = art.status === 'active' && art.is_active === 1;
        const statusBadge = isActive
          ? `<span class="badge-status-active" style="display:inline-flex; align-items:center; gap:5px; padding:4px 9px; border-radius:6px; font-size:12px; font-weight:700; background:#DCFCE7; color:#15803D;"><i class="fa-solid fa-circle-check"></i> Live on Site</span>`
          : `<span class="badge-status-hidden" style="display:inline-flex; align-items:center; gap:5px; padding:4px 9px; border-radius:6px; font-size:12px; font-weight:700; background:#F1F5F9; color:#64748B;"><i class="fa-solid fa-eye-slash"></i> Hidden (Draft)</span>`;

        const toggleBtn = isActive
          ? `<button type="button" class="btn-table-action btn-art-hide js-toggle-art-btn" data-id="${art.id}" title="Hide from public site and sitemap" style="background:#FFF1F2; color:#BE123C; border:1px solid #FECDD3; padding:5px 9px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer;">
              <i class="fa-solid fa-eye-slash"></i> Hide
            </button>`
          : `<button type="button" class="btn-table-action btn-art-publish js-toggle-art-btn" data-id="${art.id}" title="Publish to live site and sitemap" style="background:#ECFDF5; color:#047857; border:1px solid #A7F3D0; padding:5px 9px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer;">
              <i class="fa-solid fa-globe"></i> Activate
            </button>`;

        const createdDate = (art.created_at || '').substring(0, 10);

        return `
          <tr>
            <td><strong>#${art.id}</strong></td>
            <td>
              <div style="font-weight:700; color:#1E293B; margin-bottom: 3px; font-size: 13.5px;">${this.escapeHtml(art.title)}</div>
              <div style="font-size:11.5px; color:#64748B; font-family: monospace;">
                <a href="/article.html?slug=${art.slug}" target="_blank" style="color:#2563eb; text-decoration:none;">
                  /article.html?slug=${art.slug} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:10px;"></i>
                </a>
              </div>
            </td>
            <td>
              <span style="font-size:12.5px; color:#475569; display:flex; align-items:center; gap:4px;">
                <i class="fa-solid fa-location-dot" style="color:#DC2626;"></i> ${this.escapeHtml(art.geo_target || 'Toronto & GTA')}
              </span>
            </td>
            <td>
              <span style="font-size:12px; font-weight:600; color:#334155;">
                ${categoryLabels[art.category] || art.category}
              </span>
              <div style="font-size:11px; color:#94A3B8; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${this.escapeHtml(art.keywords)}">
                ${this.escapeHtml(art.keywords)}
              </div>
            </td>
            <td style="text-align: center;">${statusBadge}</td>
            <td style="text-align: center; font-weight:600; color:#475569;">
              <i class="fa-solid fa-eye" style="font-size:11px; color:#94A3B8;"></i> ${art.views || 0}
            </td>
            <td style="text-align: right;">
              <div style="display:flex; justify-content:flex-end; gap:6px; align-items:center;">
                ${toggleBtn}
                <button type="button" class="btn-table-action js-preview-art-btn" data-id="${art.id}" title="SEO & SERP Preview" style="background:#F8FAFC; border:1px solid #E2E8F0; padding:5px 8px; border-radius:6px; cursor:pointer;">
                  <i class="fa-solid fa-magnifying-glass"></i>
                </button>
                <button type="button" class="btn-table-action js-edit-art-btn" data-id="${art.id}" title="Edit Article" style="background:#F8FAFC; border:1px solid #E2E8F0; padding:5px 8px; border-radius:6px; cursor:pointer;">
                  <i class="fa-solid fa-pen"></i>
                </button>
                <button type="button" class="btn-table-action js-delete-art-btn" data-id="${art.id}" title="Delete Article" style="background:#FFF1F2; border:1px solid #FECDD3; color:#DC2626; padding:5px 8px; border-radius:6px; cursor:pointer;">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      // Bind dynamic row action buttons
      tbody.querySelectorAll('.js-toggle-art-btn').forEach(btn => {
        btn.onclick = () => this.toggleArticleStatus(parseInt(btn.dataset.id));
      });
      tbody.querySelectorAll('.js-preview-art-btn').forEach(btn => {
        btn.onclick = () => this.openArticlePreview(parseInt(btn.dataset.id));
      });
      tbody.querySelectorAll('.js-edit-art-btn').forEach(btn => {
        btn.onclick = () => this.openArticleEditor(parseInt(btn.dataset.id));
      });
      tbody.querySelectorAll('.js-delete-art-btn').forEach(btn => {
        btn.onclick = () => this.deleteArticle(parseInt(btn.dataset.id));
      });
    },

    async toggleArticleStatus(articleId) {
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/articles/${articleId}/toggle-status`, {
          method: 'PATCH',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to toggle status');

        this.showToast(data.message, data.status === 'active' ? 'success' : 'info');
        this.loadSEOArticles();
        this.loadStats();
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async openArticleEditor(articleId = null) {
      const modal = document.getElementById('modal-article-editor');
      const form = document.getElementById('form-admin-article-editor');
      if (!modal || !form) return;

      if (articleId) {
        try {
          const token = window.VicAuth.getToken();
          const res = await fetchApi(`/api/admin/articles/${articleId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const data = await res.json();
          if (!res.ok || !data.article) throw new Error(data.error || 'Failed to load article');

          const a = data.article;
          document.getElementById('art-edit-id').value = a.id;
          document.getElementById('art-modal-title').innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Edit Article #${a.id}`;
          document.getElementById('art-input-title').value = a.title || '';
          document.getElementById('art-input-slug').value = a.slug || '';
          document.getElementById('art-input-geo').value = a.geo_target || '';
          document.getElementById('art-input-category').value = a.category || 'programs';
          document.getElementById('art-input-status').value = a.status || 'hidden';
          document.getElementById('art-input-keywords').value = a.keywords || '';
          document.getElementById('art-input-summary').value = a.summary || '';
          document.getElementById('art-input-content').value = a.content || '';
          document.getElementById('art-modal-submit-btn').textContent = 'Update Article';
          modal.classList.add('active');
        } catch (err) {
          this.showToast(err.message, 'error');
        }
      } else {
        // New manual article
        form.reset();
        document.getElementById('art-edit-id').value = '';
        document.getElementById('art-modal-title').innerHTML = `<i class="fa-solid fa-plus"></i> Add New SEO Article`;
        document.getElementById('art-input-status').value = 'hidden';
        document.getElementById('art-input-geo').value = 'Toronto & GTA, Ontario';
        document.getElementById('art-modal-submit-btn').textContent = 'Create Article (Hidden by Default)';
        modal.classList.add('active');
      }
    },

    async openArticlePreview(articleId) {
      const modal = document.getElementById('modal-article-preview');
      if (!modal) return;

      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/articles/${articleId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok || !data.article) throw new Error(data.error || 'Failed to load article');

        const a = data.article;
        currentPreviewArticle = a;

        document.getElementById('preview-serp-title').textContent = a.meta_title || a.title;
        document.getElementById('preview-serp-url').textContent = `https://viccollege.ca › article › ${a.slug}`;
        document.getElementById('preview-serp-desc').textContent = a.meta_description || a.summary || 'Victoria International College career diploma information and grants.';
        document.getElementById('preview-serp-geo').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${this.escapeHtml(a.geo_target || 'Toronto, Ontario')}`;
        
        const serpStatus = document.getElementById('preview-serp-status');
        if (serpStatus) {
          serpStatus.innerHTML = a.status === 'active' 
            ? '<span style="color:#15803d; font-weight:700;">🟢 Live in Google Sitemap</span>' 
            : '<span style="color:#dc2626; font-weight:700;">🔒 Hidden / Draft</span>';
        }

        document.getElementById('preview-reader-title').textContent = a.title;
        document.getElementById('preview-reader-body').innerHTML = a.content;

        const togglePublishBtn = document.getElementById('btn-preview-toggle-publish');
        if (togglePublishBtn) {
          if (a.status === 'active') {
            togglePublishBtn.innerHTML = '<i class="fa-solid fa-eye-slash"></i> Hide Article';
            togglePublishBtn.style.background = '#dc2626';
          } else {
            togglePublishBtn.innerHTML = '<i class="fa-solid fa-globe"></i> Activate / Publish Article';
            togglePublishBtn.style.background = '#059669';
          }
        }

        modal.classList.add('active');
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async deleteArticle(articleId) {
      if (!confirm(`Are you sure you want to permanently delete article #${articleId}?`)) return;

      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi(`/api/admin/articles/${articleId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to delete article');

        this.showToast(data.message || 'Article deleted successfully.', 'success');
        this.loadSEOArticles();
        this.loadStats();
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async syncSitemap() {
      try {
        const token = window.VicAuth.getToken();
        const res = await fetchApi('/api/admin/sitemap/generate', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to sync sitemap');

        this.showToast(`✅ ${data.message}`, 'success');
        this.loadStats();
        this.loadSEOArticles();
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async inspectSitemap() {
      const modal = document.getElementById('modal-sitemap-viewer');
      const pre = document.getElementById('sitemap-xml-pre');
      const stats = document.getElementById('sitemap-modal-stats');
      if (!modal || !pre) return;

      modal.classList.add('active');
      pre.textContent = 'Fetching current /sitemap.xml...';

      try {
        const res = await fetchApi('/sitemap.xml');
        const xml = await res.text();
        pre.textContent = xml;

        const countMatches = (xml.match(/<url>/g) || []).length;
        if (stats) stats.textContent = `Total Indexed URLs: ${countMatches}`;
      } catch (err) {
        pre.textContent = 'Error loading sitemap.xml: ' + err.message;
      }
    },

    async safeJson(res) {
      const text = await res.text();
      if (!text || !text.trim()) return {};
      try {
        return JSON.parse(text);
      } catch (err) {
        if (text.startsWith('<!doctype') || text.startsWith('<html') || text.includes('<!DOCTYPE')) {
          throw new Error(`Server returned HTML page instead of API JSON (HTTP ${res.status}). Verify you are connected to http://localhost:5055.`);
        }
        throw new Error(`Invalid server response: ${text.substring(0, 120)}`);
      }
    },

    escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    },

    showToast(msg, type = 'info') {
      if (window.VicAuth) {
        window.VicAuth.showToast(msg, type);
      } else {
        alert(msg);
      }
    }
  };

  window.AdminApp = AdminApp;
  document.addEventListener('DOMContentLoaded', () => {
    AdminApp.init();
  });
})();
