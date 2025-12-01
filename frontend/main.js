const API_BASE_URL = "http://localhost:8000"; // 필요하면 수정
const USER_KEY = "amumal-user";

// ---------- 공통 유틸 ----------

function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function isValidPassword(pwd) {
  // 8~20, 대문자/소문자/숫자/특수문자 최소 1개씩
  const re =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,20}$/;
  return re.test(pwd);
}

function isValidNickname(nickname) {
  if (!nickname) return false;
  if (nickname.length > 10) return false;
  if (/\s/.test(nickname)) return false;
  return true;
}

function setButtonActive(button, active) {
  if (!button) return;
  if (active) {
    button.classList.add("active");
    button.disabled = false;
  } else {
    button.classList.remove("active");
    button.disabled = true;
  }
}

function setHelper(el, message, type) {
  if (!el) return;
  el.textContent = message || "";
  el.classList.remove("helper-error", "helper-success");
  if (type === "error") el.classList.add("helper-error");
  if (type === "success") el.classList.add("helper-success");
}

// 숫자 -> 1k / 10k / 100k
function formatCount(value) {
  if (typeof value === "string") {
    const parsed = parseInt(value, 10);
    if (!isNaN(parsed)) value = parsed;
    else return value;
  }
  if (typeof value !== "number") return String(value);

  if (value >= 100000) return "100k";
  if (value >= 10000) return "10k";
  if (value >= 1000) {
    return Math.round(value / 1000) + "k";
  }
  return String(value);
}

// 제목 26자 제한
function truncateTitle(title) {
  if (!title) return "";
  return title.slice(0, 26);
}

// 세션 저장/조회
function saveUserSession(apiData, email) {
  const user = {
    user_id: apiData.user_id,
    nickname: apiData.profile_nickname,
    profile_image: apiData.profile_img_url,
    email,
  };
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function getUserSession() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function clearUserSession() {
  localStorage.removeItem(USER_KEY);
}

// 인증이 필요한 페이지 공통 초기화
function initAuthedPage() {
  const user = getUserSession();
  if (!user) {
    window.location.href = "login.html";
    return null;
  }
  initHeaderWithProfile(user);
  return user;
}

// ---------- 헤더 프로필/로그아웃 ----------

function initHeaderWithProfile(user) {
  const profileBtn = document.getElementById(
    "header-profile-btn"
  );
  const profileMenu = document.getElementById(
    "header-profile-menu"
  );
  if (!profileBtn || !profileMenu) return;

  // 이미지 or 이니셜
  if (user.profile_image) {
    const img = document.createElement("img");
    img.src = user.profile_image;
    profileBtn.innerHTML = "";
    profileBtn.appendChild(img);
  } else {
    profileBtn.innerHTML = "";
    const span = document.createElement("span");
    span.className = "header-profile-initial";
    span.textContent = user.nickname
      ? user.nickname[0].toUpperCase()
      : "U";
    profileBtn.appendChild(span);
  }

  const toggleMenu = () => {
    profileMenu.classList.toggle("hidden");
  };

  profileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  document.addEventListener("click", () => {
    profileMenu.classList.add("hidden");
  });

  profileMenu.addEventListener("click", (e) => {
    e.stopPropagation();
    const action = e.target.dataset.action;
    if (!action) return;

    if (action === "edit-profile") {
      window.location.href = "profile_edit.html";
    } else if (action === "edit-password") {
      window.location.href = "password_edit.html";
    } else if (action === "logout") {
      handleLogout(user);
    }
  });
}

async function handleLogout(user) {
  if (!user) return;
  try {
    await fetch(
      `${API_BASE_URL}/user/logout/${user.user_id}`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );
  } catch (e) {
    console.error(e);
  } finally {
    clearUserSession();
    window.location.href = "login.html";
  }
}

// ---------- 로그인 페이지 ----------

function initLoginPage() {
  const emailInput = document.getElementById("login-email");
  const pwdInput = document.getElementById("login-password");
  const emailHelper = document.getElementById(
    "login-email-helper"
  );
  const pwdHelper = document.getElementById(
    "login-password-helper"
  );
  const formHelper = document.getElementById(
    "login-form-helper"
  );
  const loginBtn = document.getElementById("login-btn");
  const signupBtn = document.getElementById("go-signup-btn");

  let emailValid = false;
  let pwdValid = false;

  function updateLoginButton() {
    setButtonActive(loginBtn, emailValid && pwdValid);
  }

  emailInput.addEventListener("blur", () => {
    const value = emailInput.value.trim();
    if (!value || !isValidEmail(value)) {
      emailValid = false;
      setHelper(
        emailHelper,
        "올바른 이메일 주소 형식을 입력해주세요.",
        "error"
      );
    } else {
      emailValid = true;
      setHelper(emailHelper, "");
    }
    updateLoginButton();
  });

  pwdInput.addEventListener("blur", () => {
    const value = pwdInput.value;
    if (!value) {
      pwdValid = false;
      setHelper(
        pwdHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
    } else if (!isValidPassword(value)) {
      pwdValid = false;
      setHelper(
        pwdHelper,
        "8자 이상 20자 이하이고 대문자, 소문자, 숫자, 특수문자를 최소 1개씩 포함하세요",
        "error"
      );
    } else {
      pwdValid = true;
      setHelper(pwdHelper, "");
    }
    updateLoginButton();
  });

  [emailInput, pwdInput].forEach((el) =>
    el.addEventListener("input", () => {
      updateLoginButton();
      setHelper(formHelper, "");
    })
  );

  loginBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!(emailValid && pwdValid)) return;

    const payload = {
      email: emailInput.value.trim(),
      password: pwdInput.value,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/user/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (res.status === 200) {
        const data = await res.json();
        if (data.detail === "login_success") {
          saveUserSession(data.data, payload.email);
          window.location.href = "posts.html";
          return;
        }
      }

      setHelper(
        formHelper,
        "아이디 또는 비밀번호를 확인해주세요",
        "error"
      );
    } catch (err) {
      console.error(err);
      setHelper(
        formHelper,
        "아이디 또는 비밀번호를 확인해주세요",
        "error"
      );
    }
  });

  signupBtn.addEventListener("click", () => {
    window.location.href = "signup.html";
  });
}

// ---------- 회원가입 페이지 ----------

function initSignupPage() {
  const backBtn = document.getElementById("signup-back-btn");
  const toLoginBtn = document.getElementById(
    "signup-go-login-btn"
  );

  const emailInput = document.getElementById("signup-email");
  const emailHelper = document.getElementById(
    "signup-email-helper"
  );

  const pwdInput = document.getElementById("signup-password");
  const pwdHelper = document.getElementById(
    "signup-password-helper"
  );

  const pwdConfirmInput = document.getElementById(
    "signup-password-confirm"
  );
  const pwdConfirmHelper = document.getElementById(
    "signup-password-confirm-helper"
  );

  const nicknameInput = document.getElementById(
    "signup-nickname"
  );
  const nicknameHelper = document.getElementById(
    "signup-nickname-helper"
  );

  const signupBtn = document.getElementById("signup-btn");

  const profileCircle = document.getElementById(
    "profile-circle"
  );
  const profileInput = document.getElementById(
    "profile-file-input"
  );
  const profileHelper = document.getElementById(
    "profile-helper"
  );

  let profileImagePath = null;
  let emailValid = false;
  let emailAvailable = false;
  let pwdValid = false;
  let pwdConfirmValid = false;
  let nicknameValid = false;
  let nicknameAvailable = false;

  function updateSignupButton() {
    const canSubmit =
      emailValid &&
      emailAvailable &&
      pwdValid &&
      pwdConfirmValid &&
      nicknameValid &&
      nicknameAvailable;
    setButtonActive(signupBtn, canSubmit);
  }

  const goLogin = () => (window.location.href = "login.html");
  backBtn.addEventListener("click", goLogin);
  toLoginBtn.addEventListener("click", goLogin);

  // 이메일
  emailInput.addEventListener("blur", async () => {
    const value = emailInput.value.trim();
    emailAvailable = false;

    if (!value || !isValidEmail(value)) {
      emailValid = false;
      setHelper(
        emailHelper,
        "올바른 이메일 주소 형식을 입력해주세요.",
        "error"
      );
      updateSignupButton();
      return;
    }

    emailValid = true;

    try {
      const res = await fetch(
        `${API_BASE_URL}/user/check-email?email=${encodeURIComponent(
          value
        )}`,
        { method: "GET", credentials: "include" }
      );

      if (res.status === 200) {
        const data = await res.json();
        if (data.data && data.data.possible) {
          emailAvailable = true;
          setHelper(
            emailHelper,
            "사용가능한 이메일입니다.",
            "success"
          );
        } else {
          emailAvailable = false;
          setHelper(
            emailHelper,
            "중복된 이메일 입니다.",
            "error"
          );
        }
      } else if (res.status === 400) {
        emailValid = false;
        setHelper(
          emailHelper,
          "올바른 이메일 주소 형식을 입력해주세요.",
          "error"
        );
      } else {
        emailAvailable = false;
        setHelper(
          emailHelper,
          "이메일 확인 중 오류가 발생했습니다.",
          "error"
        );
      }
    } catch (err) {
      console.error(err);
      emailAvailable = false;
      setHelper(
        emailHelper,
        "이메일 확인 중 오류가 발생했습니다.",
        "error"
      );
    }

    updateSignupButton();
  });

  // 비밀번호
  pwdInput.addEventListener("blur", () => {
    const value = pwdInput.value;

    if (!value) {
      pwdValid = false;
      setHelper(
        pwdHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
    } else if (!isValidPassword(value)) {
      pwdValid = false;
      setHelper(
        pwdHelper,
        "8자 이상 20자 이하이고 대문자, 소문자, 숫자, 특수문자를 최소 1개씩 포함하세요",
        "error"
      );
    } else {
      pwdValid = true;
      setHelper(pwdHelper, "");
    }

    validatePasswordConfirm();
    updateSignupButton();
  });

  function validatePasswordConfirm() {
    const v = pwdConfirmInput.value;

    if (!v) {
      pwdConfirmValid = false;
      setHelper(
        pwdConfirmHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
      return;
    }
    if (v !== pwdInput.value) {
      pwdConfirmValid = false;
      setHelper(
        pwdConfirmHelper,
        "비밀번호가 다릅니다",
        "error"
      );
    } else {
      pwdConfirmValid = true;
      setHelper(pwdConfirmHelper, "");
    }
  }

  pwdConfirmInput.addEventListener("blur", () => {
    validatePasswordConfirm();
    updateSignupButton();
  });

  // 닉네임
  nicknameInput.addEventListener("blur", async () => {
    const value = nicknameInput.value.trim();
    nicknameAvailable = false;

    if (!value) {
      nicknameValid = false;
      setHelper(
        nicknameHelper,
        "닉네임을 입력해주세요",
        "error"
      );
      updateSignupButton();
      return;
    }

    if (!isValidNickname(value)) {
      nicknameValid = false;
      setHelper(
        nicknameHelper,
        "10자 이내, 띄어쓰기 불가",
        "error"
      );
      updateSignupButton();
      return;
    }

    nicknameValid = true;

    try {
      const res = await fetch(
        `${API_BASE_URL}/user/check-nickname?nickname=${encodeURIComponent(
          value
        )}`,
        { method: "GET", credentials: "include" }
      );

      if (res.status === 200) {
        const data = await res.json();
        if (data.data && data.data.possible) {
          nicknameAvailable = true;
          setHelper(
            nicknameHelper,
            "사용가능한 닉네임입니다.",
            "success"
          );
        } else {
          nicknameAvailable = false;
          setHelper(
            nicknameHelper,
            "중복된 닉네임입니다.",
            "error"
          );
        }
      } else if (res.status === 400) {
        nicknameValid = false;
        setHelper(
          nicknameHelper,
          "10자 이내, 띄어쓰기 불가",
          "error"
        );
      } else {
        nicknameAvailable = false;
        setHelper(
          nicknameHelper,
          "닉네임 확인 중 오류가 발생했습니다.",
          "error"
        );
      }
    } catch (err) {
      console.error(err);
      nicknameAvailable = false;
      setHelper(
        nicknameHelper,
        "닉네임 확인 중 오류가 발생했습니다.",
        "error"
      );
    }

    updateSignupButton();
  });

  // 프로필 이미지
  profileCircle.addEventListener("click", () => {
    const hasImage =
      profileCircle.querySelector("img") !== null;
    if (hasImage) {
      profileCircle.innerHTML = "<span>+</span>";
      profileImagePath = null;
      setHelper(
        profileHelper,
        "프로필 사진을 추가하세요.",
        "error"
      );
      updateSignupButton();
      return;
    }
    profileInput.click();
  });

  profileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) {
      if (!profileImagePath) {
        setHelper(
          profileHelper,
          "프로필 사진을 추가하세요.",
          "error"
        );
      }
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      profileCircle.innerHTML = "";
      const img = document.createElement("img");
      img.src = reader.result;
      profileCircle.appendChild(img);
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/image`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (res.status === 201) {
        const data = await res.json();
        if (data.data && data.data.file_path) {
          profileImagePath = data.data.file_path;
          setHelper(profileHelper, "", "");
        } else {
          profileImagePath = null;
          setHelper(
            profileHelper,
            "이미지 업로드 중 오류가 발생했습니다.",
            "error"
          );
        }
      } else {
        profileImagePath = null;
        setHelper(
          profileHelper,
          "이미지 업로드 중 오류가 발생했습니다.",
          "error"
        );
      }
    } catch (err) {
      console.error(err);
      profileImagePath = null;
      setHelper(
        profileHelper,
        "이미지 업로드 중 오류가 발생했습니다.",
        "error"
      );
    }

    updateSignupButton();
  });

  // 회원가입 요청
  signupBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const canSubmit =
      emailValid &&
      emailAvailable &&
      pwdValid &&
      pwdConfirmValid &&
      nicknameValid &&
      nicknameAvailable;

    if (!canSubmit) return;

    const payload = {
      email: emailInput.value.trim(),
      password: pwdInput.value,
      nickname: nicknameInput.value.trim(),
    };

    if (profileImagePath) {
      payload.profile_image = profileImagePath;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/user/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (res.status === 201) {
        const data = await res.json();
        if (data.detail === "register_success") {
          alert("회원가입이 완료되었습니다.");
          window.location.href = "login.html";
          return;
        }
      }

      alert(
        "회원가입에 실패했습니다. 입력 내용을 다시 확인해주세요."
      );
    } catch (err) {
      console.error(err);
      alert("회원가입 중 오류가 발생했습니다.");
    }
  });
}

// ---------- 게시글 목록 페이지 ----------

function initPostsPage() {
  const user = initAuthedPage();
  if (!user) return;

  const listEl = document.getElementById("posts-list");
  const loadingEl = document.getElementById(
    "posts-loading"
  );
  const writeBtn = document.getElementById("btn-write");

  let cursorId = 0;
  const PAGE_SIZE = 10;
  let isLoading = false;
  let hasMore = true;

  writeBtn.addEventListener("click", () => {
    window.location.href = "post_write.html"; // 나중에 만들 페이지
  });

  async function fetchPosts() {
    if (isLoading || !hasMore) return;
    isLoading = true;
    loadingEl.textContent = "불러오는 중...";

    try {
      const res = await fetch(
        `${API_BASE_URL}/posts?cursor_id=${cursorId}&count=${PAGE_SIZE}`,
        { method: "GET", credentials: "include" }
      );

      if (res.status !== 200) {
        loadingEl.textContent = "";
        hasMore = false;
        return;
      }

      const data = await res.json();
      if (
        !data.data ||
        !Array.isArray(data.data.post_list)
      ) {
        hasMore = false;
        loadingEl.textContent = "";
        return;
      }

      const posts = data.data.post_list;
      posts.forEach((post) => {
        const card = document.createElement("article");
        card.className = "post-card";
        card.dataset.postId = post.post_id;

        const title = truncateTitle(post.title || "");
        const views = formatCount(post.views);
        const likes = formatCount(post.likes);
        const comments = formatCount(post.comments_count);

        card.innerHTML = `
          <div class="post-title">${title}</div>
          <div class="post-meta-row">
            <div>좋아요 ${likes} · 댓글 ${comments} · 조회수 ${views}</div>
            <div>${post.created_at}</div>
          </div>
          <div class="post-summary">${post.summary || ""}</div>
          <div class="post-author-row">
            <div class="post-author-avatar"></div>
            <div>${post.author_nickname}</div>
          </div>
        `;

        card.addEventListener("click", () => {
          window.location.href = `post_detail.html?post_id=${post.post_id}`;
        });

        listEl.appendChild(card);
      });

      if (data.data.next_cursor != null) {
        cursorId = data.data.next_cursor;
        hasMore = true;
        loadingEl.textContent = "아래로 스크롤하면 더 불러옵니다.";
      } else {
        hasMore = false;
        loadingEl.textContent = "더 이상 게시글이 없습니다.";
      }
    } catch (err) {
      console.error(err);
      loadingEl.textContent = "게시글을 불러오지 못했습니다.";
      hasMore = false;
    } finally {
      isLoading = false;
    }
  }

  // 최초 로드
  fetchPosts();

  // 인피니티 스크롤
  window.addEventListener("scroll", () => {
    if (!hasMore || isLoading) return;
    const scrollBottom =
      window.innerHeight + window.scrollY;
    if (scrollBottom >= document.body.offsetHeight - 200) {
      fetchPosts();
    }
  });
}

// ---------- 회원정보 수정 페이지 ----------

function initProfileEditPage() {
  const user = initAuthedPage();
  if (!user) return;

  const emailInput = document.getElementById(
    "profile-email"
  );
  const nicknameInput = document.getElementById(
    "profile-nickname"
  );
  const nicknameHelper = document.getElementById(
    "profile-nickname-helper"
  );
  const updateBtn = document.getElementById(
    "profile-update-btn"
  );

  const profileCircle = document.getElementById(
    "profile-circle"
  );
  const profileInput = document.getElementById(
    "profile-file-input"
  );
  const profileHelper = document.getElementById(
    "profile-helper"
  );

  const toast = document.getElementById("toast");
  const toastBtn = document.getElementById(
    "toast-confirm-btn"
  );

  const modalBackdrop = document.getElementById(
    "delete-modal-backdrop"
  );
  const modalCancel = document.getElementById(
    "modal-btn-cancel"
  );
  const modalConfirm = document.getElementById(
    "modal-btn-confirm"
  );
  const deleteBtn = document.getElementById(
    "btn-delete-user"
  );

  let nicknameValid = true;
  let nicknameAvailable = true;
  let profileImagePath = user.profile_image || null;

  // 초기 값 세팅
  emailInput.value = user.email || "";
  nicknameInput.value = user.nickname || "";

  if (user.profile_image) {
    profileCircle.innerHTML = "";
    const img = document.createElement("img");
    img.src = user.profile_image;
    profileCircle.appendChild(img);
    setHelper(profileHelper, "", "");
  } else {
    profileCircle.innerHTML = "<span>+</span>";
    setHelper(
      profileHelper,
      "프로필 사진을 추가하세요.",
      "error"
    );
  }

  function updateButton() {
    const can =
      nicknameValid && nicknameAvailable && nicknameInput.value.trim();
    setButtonActive(updateBtn, !!can);
  }

  // 닉네임 blur 시 유효성 + 중복
  nicknameInput.addEventListener("blur", async () => {
    const value = nicknameInput.value.trim();
    nicknameAvailable = false;

    if (!value) {
      nicknameValid = false;
      setHelper(
        nicknameHelper,
        "닉네임을 입력해주세요",
        "error"
      );
      updateButton();
      return;
    }

    if (!isValidNickname(value)) {
      nicknameValid = false;
      setHelper(
        nicknameHelper,
        "10자 이내, 띄어쓰기 불가",
        "error"
      );
      updateButton();
      return;
    }

    nicknameValid = true;

    // 기존 닉네임이면 굳이 중복확인 안 함
    if (value === user.nickname) {
      nicknameAvailable = true;
      setHelper(nicknameHelper, "", "");
      updateButton();
      return;
    }

    try {
      const res = await fetch(
        `${API_BASE_URL}/user/check-nickname?nickname=${encodeURIComponent(
          value
        )}`,
        { method: "GET", credentials: "include" }
      );

      if (res.status === 200) {
        const data = await res.json();
        if (data.data && data.data.possible) {
          nicknameAvailable = true;
          setHelper(
            nicknameHelper,
            "사용가능한 닉네임입니다.",
            "success"
          );
        } else {
          nicknameAvailable = false;
          setHelper(
            nicknameHelper,
            "중복된 닉네임입니다.",
            "error"
          );
        }
      } else if (res.status === 400) {
        nicknameValid = false;
        setHelper(
          nicknameHelper,
          "10자 이내, 띄어쓰기 불가",
          "error"
        );
      } else {
        nicknameAvailable = false;
        setHelper(
          nicknameHelper,
          "닉네임 확인 중 오류가 발생했습니다.",
          "error"
        );
      }
    } catch (err) {
      console.error(err);
      nicknameAvailable = false;
      setHelper(
        nicknameHelper,
        "닉네임 확인 중 오류가 발생했습니다.",
        "error"
      );
    }

    updateButton();
  });

  // 프로필 이미지 클릭/업로드
  profileCircle.addEventListener("click", () => {
    const hasImage =
      profileCircle.querySelector("img") !== null;
    if (hasImage) {
      profileCircle.innerHTML = "<span>+</span>";
      profileImagePath = null;
      setHelper(
        profileHelper,
        "프로필 사진을 추가하세요.",
        "error"
      );
      updateButton();
      return;
    }
    profileInput.click();
  });

  profileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) {
      if (!profileImagePath) {
        setHelper(
          profileHelper,
          "프로필 사진을 추가하세요.",
          "error"
        );
      }
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      profileCircle.innerHTML = "";
      const img = document.createElement("img");
      img.src = reader.result;
      profileCircle.appendChild(img);
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/image`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (res.status === 201) {
        const data = await res.json();
        if (data.data && data.data.file_path) {
          profileImagePath = data.data.file_path;
          setHelper(profileHelper, "", "");
        } else {
          profileImagePath = null;
          setHelper(
            profileHelper,
            "이미지 업로드 중 오류가 발생했습니다.",
            "error"
          );
        }
      } else {
        profileImagePath = null;
        setHelper(
          profileHelper,
          "이미지 업로드 중 오류가 발생했습니다.",
          "error"
        );
      }
    } catch (err) {
      console.error(err);
      profileImagePath = null;
      setHelper(
        profileHelper,
        "이미지 업로드 중 오류가 발생했습니다.",
        "error"
      );
    }

    updateButton();
  });

  // 수정 완료 토스트에서 확인 누르면 목록으로
  toastBtn.addEventListener("click", () => {
    toast.classList.add("hidden");
    window.location.href = "posts.html";
  });

  // 회원정보 수정 요청
  updateBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!nicknameValid || !nicknameAvailable) return;

    const payload = {
      nickname: nicknameInput.value.trim(),
    };
    if (profileImagePath) {
      payload.profile_image = profileImagePath;
    }

    try {
      const res = await fetch(
        `${API_BASE_URL}/user/update-me/${user.user_id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        }
      );

      if (res.status === 200) {
        const data = await res.json();
        if (data.detail === "profile_update_success") {
          // 로컬 세션도 업데이트
          const updated = {
            ...user,
            nickname: data.data.nickname,
            profile_image: data.data.profile_image,
          };
          localStorage.setItem(
            USER_KEY,
            JSON.stringify(updated)
          );
          toast.classList.remove("hidden");
          return;
        }
      }

      alert("회원정보 수정에 실패했습니다.");
    } catch (err) {
      console.error(err);
      alert("회원정보 수정 중 오류가 발생했습니다.");
    }
  });

  // 회원 탈퇴 모달
  deleteBtn.addEventListener("click", () => {
    modalBackdrop.classList.remove("hidden");
  });

  modalCancel.addEventListener("click", () => {
    modalBackdrop.classList.add("hidden");
  });

  modalBackdrop.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) {
      modalBackdrop.classList.add("hidden");
    }
  });

  modalConfirm.addEventListener("click", async () => {
    try {
      const res = await fetch(
        `${API_BASE_URL}/user/${user.user_id}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      if (res.status === 200) {
        clearUserSession();
        window.location.href = "login.html";
        return;
      }

      alert("회원 탈퇴에 실패했습니다.");
    } catch (err) {
      console.error(err);
      alert("회원 탈퇴 중 오류가 발생했습니다.");
    }
  });

  updateButton();
}

// ---------- 비밀번호 수정 페이지 ----------

function initPasswordEditPage() {
  const user = initAuthedPage();
  if (!user) return;

  const currentInput = document.getElementById(
    "pwd-current"
  );
  const newInput = document.getElementById("pwd-new");
  const confirmInput = document.getElementById(
    "pwd-confirm"
  );

  const currentHelper = document.getElementById(
    "pwd-current-helper"
  );
  const newHelper = document.getElementById(
    "pwd-new-helper"
  );
  const confirmHelper = document.getElementById(
    "pwd-confirm-helper"
  );

  const updateBtn = document.getElementById(
    "pwd-update-btn"
  );

  let currentValid = false;
  let newValid = false;
  let confirmValid = false;

  function updateBtnState() {
    const can =
      currentValid && newValid && confirmValid;
    setButtonActive(updateBtn, can);
  }

  currentInput.addEventListener("blur", () => {
    if (!currentInput.value) {
      currentValid = false;
      setHelper(
        currentHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
    } else {
      currentValid = true;
      setHelper(currentHelper, "");
    }
    updateBtnState();
  });

  newInput.addEventListener("blur", () => {
    const v = newInput.value;
    if (!v) {
      newValid = false;
      setHelper(
        newHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
    } else if (!isValidPassword(v)) {
      newValid = false;
      setHelper(
        newHelper,
        "8자 이상 20자 이하이고 대문자, 소문자, 숫자, 특수문자를 최소 1개씩 포함하세요",
        "error"
      );
    } else {
      newValid = true;
      setHelper(newHelper, "");
    }
    validateConfirm();
    updateBtnState();
  });

  function validateConfirm() {
    const v = confirmInput.value;
    if (!v) {
      confirmValid = false;
      setHelper(
        confirmHelper,
        "비밀번호를 입력해주세요",
        "error"
      );
      return;
    }
    if (v !== newInput.value) {
      confirmValid = false;
      setHelper(
        confirmHelper,
        "비밀번호가 다릅니다",
        "error"
      );
    } else {
      confirmValid = true;
      setHelper(confirmHelper, "");
    }
  }

  confirmInput.addEventListener("blur", () => {
    validateConfirm();
    updateBtnState();
  });

  updateBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!(currentValid && newValid && confirmValid))
      return;

    const payload = {
      current_password: currentInput.value,
      new_password: newInput.value,
    };

    try {
      const res = await fetch(
        `${API_BASE_URL}/user/update-password/${user.user_id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        }
      );

      if (res.status === 200) {
        const data = await res.json();
        if (data.detail === "password_update_success") {
          alert("비밀번호가 변경되었습니다.");
          window.location.href = "posts.html";
          return;
        }
      } else if (res.status === 400) {
        const data = await res.json();
        if (data.detail === "invalid_password") {
          setHelper(
            currentHelper,
            "현재 비밀번호가 올바르지 않습니다.",
            "error"
          );
          currentValid = false;
          updateBtnState();
          return;
        }
      }

      alert("비밀번호 변경에 실패했습니다.");
    } catch (err) {
      console.error(err);
      alert("비밀번호 변경 중 오류가 발생했습니다.");
    }
  });

  updateBtnState();
}

// ---------- 페이지별 초기화 ----------

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "login") {
    initLoginPage();
  } else if (page === "signup") {
    initSignupPage();
  } else if (page === "posts") {
    initPostsPage();
  } else if (page === "profile-edit") {
    initProfileEditPage();
  } else if (page === "password-edit") {
    initPasswordEditPage();
  }
});
