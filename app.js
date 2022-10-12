const sections = document.querySelectorAll('.section');
const sectBtns = document.querySelectorAll('.controlls');
const sectBtn = document.querySelectorAll('.control');
const allSections = document.querySelector('.main-content');
const submit_btn = document.querySelector('.main-btn1');



function PageTransitions(){
  //Button click active class

  for(let i=0; i<sectBtn.length; i++){
    sectBtn[i].addEventListener('click',function(){
        let currentBtn = document.querySelectorAll('.active-btn');
        currentBtn[0].className = currentBtn[0].className.replace('active-btn', '');
        this.className += ' active-btn';
    }
    
    )
  }
  //section active class
  allSections.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    if(id){
      //remove selected from the other btns
      sectBtns.forEach((btn) => {
        btn.classList.remove('active')
      })
      e.target.classList.add('active')

      //hide other sections
      sections.forEach((section)=>{
        section.classList.remove('active')
      })
      const element = document.getElementById(id);
      element.classList.add('active');
    }
  })
}

PageTransitions();



// function email_page(){
//   submit_btn.addEventListener('click', (e) => {
//   // e.preventDefault();
//   const id = e.target.dataset.id;
//   // console.log(msg);
//   // var name=document.getElementById('name').value;
//   // var user=document.getElementById('email').value;
//   // var subject=document.getElementById('subject').vlaue;
//   // var msg=document.getElementById('body').value;
//    console.log('hi');

// //   Email.send({
// //     Host : "smtp.gmail.com",
// //     Username : "zubairhossain773@gmail.com",
// //     Password : "qhnfevsahjlipnpu",
// //     To : 'zubairhossain773@gmail.com',
// //     From : user,
// //     Subject : subject,
// //     Body : msg
// // }).then(
// //   message => alert(message)
// // );
// })

// }

// email_page();

// function email_page(){
//   submit_btn.addEventListener('click', (e) => {
//   e.preventDefault()
//   var name=document.getElementById('name').value;
//   var user=document.getElementById('email').value;
//   var subjt=document.getElementById('sub').value;
//   var msg=document.getElementById('body').value;

//   // console.log(name);
//   // console.log(user);
//   // console.log(subjt);
//   // console.log(msg);
  
//     Email.send({
//     Host : "smtp.elasticemail.com",
//     Username : "zubairhossain773@gmail.com",
//     Password : "DFF361788149896F4D4F7CC56B7FB0EAFB81",
//     To : 'zubairhossain773@gmail.com',
//     From : 'mzh706@gmail.com',
//     Subject : subjt,
//     Body : msg
// }).then(
//   message => alert(message)
// );

// })

// }

// email_page();