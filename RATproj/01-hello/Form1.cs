using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net.Sockets; // for listeners and sockets
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace hello
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            this.Hide();

            // creat listener
            TcpListener tcpListener = new TcpListener(System.Net.IPAddress.Any, 4444); // can conn with any ip addr
            tcpListener.Start();

            // creat the pipe
            Socket socketForClient = tcpListener.AcceptSocket();
            NetworkStream networkStream = new NetworkStream(socketForClient);
            StreamReader streamReader = new StreamReader(networkStream);

            string line = streamReader.ReadLine();
            if (line.LastIndexOf("m") != -1) MessageBox.Show("Hello");

            // close pipe 
            streamReader.Close();
            networkStream.Close();
            socketForClient.Close();
            // close program
            System.Environment.Exit(0);
        }
    }
}
